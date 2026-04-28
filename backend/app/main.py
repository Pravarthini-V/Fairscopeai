from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import io
from typing import Dict, List, Optional
import uuid
import sys
import os

# Add the current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import from correct paths based on your folder structure
from app.agents.schema_agent import SchemaAgent
from app.agents.context_agent import ContextAgent
from app.agents.fairness_agent import FairnessAgent
from app.agents.correction_agent import CorrectionAgent
from app.agents.explanation_agent import ExplanationAgent
from app.rules.bias_rules import BiasRulesEngine
from app.memory.rag_storage import RAGStorage
from app.memory.user_memory import UserMemory

app = FastAPI(title="Fairness Detection System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
print("Initializing agents...")
schema_agent = SchemaAgent()
context_agent = ContextAgent()
fairness_agent = FairnessAgent()
correction_agent = CorrectionAgent()
explanation_agent = ExplanationAgent()
bias_rules = BiasRulesEngine()
rag_storage = RAGStorage()
user_memory = UserMemory()
print("All agents initialized!")

# Helper function to convert numpy types to Python native types
def convert_numpy(obj):
    """Recursively convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {str(k): convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

class AnalysisResult(BaseModel):
    user_id: str
    domain: str
    table_names: List[str]
    sensitive_columns: List[str]
    fairness_score: float
    is_fair: bool
    metrics: Dict
    explanation: str
    corrected: bool
    session_id: str

class CorrectionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    method: str = "reweight"
    sensitive_attribute: Optional[str] = None
    target_column: Optional[str] = None

@app.post("/analyze")
async def analyze_data(file: UploadFile = File(...), user_id: Optional[str] = None):
    """Main endpoint for fairness analysis"""
    try:
        print(f"\n{'='*60}")
        print(f"Analyzing file: {file.filename}")
        
        # Read file
        contents = await file.read()
        
        # Determine file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Generate user ID if not provided
        if not user_id:
            user_id = str(uuid.uuid4())
        
        # Store data in memory
        user_memory.store_data(user_id, df)
        
        # Step 1: Schema Agent
        print("\n[1/6] Schema Agent: Detecting tables...")
        table_names = schema_agent.retrieve_tables(df)
        table_name_list = [t.get("table_name", f"table_{i}") for i, t in enumerate(table_names)]
        print(f"  → Tables: {table_name_list}")
        
        # Step 2: Context Agent
        print("\n[2/6] Context Agent: Identifying domain...")
        domain = context_agent.identify_domain(df)
        print(f"  → Domain: {domain}")
        
        sensitive_columns = context_agent.get_sensitive_columns(df)
        print(f"  → Sensitive columns: {sensitive_columns}")
        
        # Step 3: Bias Rules
        print("\n[3/6] Bias Rules Engine: Loading rules...")
        domain_rules = bias_rules.get_domain_rules(domain)
        if not sensitive_columns:
            sensitive_columns = domain_rules.get("sensitive_attrs", [])
        print(f"  → Final sensitive attrs: {sensitive_columns}")
        
        # Step 4: Fairness Agent
        print("\n[4/6] Fairness Agent: Calculating...")
        if sensitive_columns:
            fairness_result = fairness_agent.calculate_fairness(df, sensitive_columns)
        else:
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()[:3]
            fairness_result = fairness_agent.calculate_fairness(df, categorical_cols)
        
        # Convert fairness result to native types
        fairness_result = convert_numpy(fairness_result)
        
        print(f"  → Score: {fairness_result['score']:.2f}")
        print(f"  → Is fair: {fairness_result['is_fair']}")
        
        # Find target column
        target_column = df.columns[-1]
        for col in df.columns:
            if any(word in col.lower() for word in ['target', 'outcome', 'result', 'decision', 'approved', 'label']):
                target_column = col
                break
        
        # Step 5: Store in RAG
        print("\n[5/6] RAG Storage: Storing session...")
        
        session_data = convert_numpy({
            "domain": domain,
            "sensitive_columns": sensitive_columns,
            "fairness_result": fairness_result,
            "filename": file.filename
        })
        rag_storage.store_session(user_id, session_data)
        
        # Store bias pattern if bias detected
        bias_pattern_stored = None
        if not fairness_result['is_fair']:
            bias_pattern = convert_numpy({
                "domain": domain,
                "sensitive_attrs": sensitive_columns,
                "fairness_score": fairness_result['score'],
                "metrics": fairness_result.get('metrics', {}),
                "timestamp": pd.Timestamp.now().isoformat()
            })
            bias_pattern_stored = rag_storage.store_bias_pattern(bias_pattern)
            print(f"  → Bias pattern stored: {bias_pattern_stored}")
        
        # Get RAG insights
        rag_insights = {
            "similar_sessions_found": len(rag_storage.retrieve_similar_sessions(
                f"domain:{domain}", user_id
            )),
            "bias_patterns_found": len(rag_storage.retrieve_similar_bias_patterns(
                domain, sensitive_columns[0] if sensitive_columns else "general"
            )),
            "bias_pattern_stored": bias_pattern_stored
        }
        
        # Step 6: Correction if needed
        corrected = False
        if not fairness_result['is_fair']:
            print("\n[6/6] Fairness FAILED - Applying correction...")
            df_corrected, corrected = correction_agent.correct_bias(df)
            if corrected:
                user_memory.update_data(user_id, df_corrected)
                fairness_result = convert_numpy(fairness_agent.calculate_fairness(df_corrected, sensitive_columns))
                print(f"  → New score after correction: {fairness_result['score']:.2f}")
        else:
            print("\n[6/6] Fairness PASSED - No correction needed")
        
        # Generate explanation
        print("Generating AI explanation...")
        explanation = explanation_agent.generate_explanation(fairness_result, rag_insights)
        print(f"  → Explanation generated")
        
        # Update history
        rag_storage.update_user_fairness_history(user_id, fairness_result)
        
        # Store final session
        final_session = convert_numpy({
            "domain": domain,
            "table_names": table_name_list,
            "sensitive_columns": sensitive_columns,
            "fairness_result": fairness_result,
            "corrected": corrected,
            "explanation": explanation,
            "rag_insights": rag_insights
        })
        session_id = rag_storage.store_session(user_id, final_session)
        
        print(f"\n✅ Analysis complete! Session: {session_id}")
        print(f"{'='*60}\n")
        
        return convert_numpy({
            "user_id": user_id,
            "filename": file.filename,
            "domain": domain,
            "table_names": table_name_list,
            "tables": table_names,
            "sensitive_columns": sensitive_columns,
            "sensitive_attributes": sensitive_columns,
            "fairness_score": float(fairness_result['score']),
            "is_fair": bool(fairness_result['is_fair']),
            "metrics": fairness_result['metrics'],
            "explanation": explanation,
            "gemini_analysis": explanation,
            "corrected": corrected,
            "is_corrected": corrected,
            "session_id": session_id,
            "target_column": str(target_column),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist()[:10],
            "rag_insights": rag_insights
        })
    
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/correct")
async def correct_data(request: CorrectionRequest):
    """Endpoint for data correction"""
    try:
        df = user_memory.get_data(request.user_id)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for user")
        
        df_corrected, success = correction_agent.correct_bias(df, request.method)
        
        if success:
            user_memory.update_data(request.user_id, df_corrected)
            
            sensitive_columns = context_agent.get_sensitive_columns(df_corrected)
            fairness_result = convert_numpy(fairness_agent.calculate_fairness(df_corrected, sensitive_columns))
            
            correction_explanation = explanation_agent.generate_correction_explanation(
                {"score": 0}, fairness_result, request.method
            )
            
            return convert_numpy({
                "status": "success",
                "message": "Data corrected successfully",
                "new_fairness_score": float(fairness_result.get('score', 0.5)),
                "is_fair": bool(fairness_result.get('is_fair', False)),
                "metrics": fairness_result.get('metrics', {}),
                "explanation": correction_explanation,
                "method_used": request.method,
                "corrected_data_preview": {
                    "rows": len(df_corrected),
                    "preview_data": df_corrected.head(5).to_dict('records')
                }
            })
        
        return {"status": "failed", "message": "Correction could not be applied"}
        
    except Exception as e:
        print(f"Correction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_user_history(user_id: str):
    """Get user's analysis history from RAG"""
    history = rag_storage.get_user_history(user_id)
    return {"user_id": user_id, "sessions": len(history), "history": history}

@app.get("/patterns")
async def get_bias_patterns():
    """Get all stored bias patterns"""
    patterns = list(rag_storage.pattern_data.values())
    return {"patterns": len(patterns), "data": patterns}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "sessions_stored": len(rag_storage.session_data),
        "bias_patterns_stored": len(rag_storage.pattern_data)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🤖 AI Fairness Detection System")
    print("="*60)
    print(f"📍 API: http://localhost:8000")
    print(f"❤️  Health: http://localhost:8000/health")
    print(f"📊 Analyze: POST http://localhost:8000/analyze")
    print(f"🔧 Correct: POST http://localhost:8000/api/correct")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")