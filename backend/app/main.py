from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
from io import StringIO
import os
import tempfile
import uuid
from typing import Optional

from app.agents.schema_agent import SchemaAgent
from app.agents.context_agent import ContextAgent
from app.agents.fairness_agent import FairnessAgent
from app.agents.correction_agent import CorrectionAgent
from app.agents.explanation_agent import ExplanationAgent
from app.memory.user_memory import UserMemory
from app.memory.rag_storage import RAGStorage
from app.rules.bias_rules import BiasRulesEngine

app = FastAPI(title="FairScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

schema_agent = SchemaAgent()
context_agent = ContextAgent()
fairness_agent = FairnessAgent()
correction_agent = CorrectionAgent()
explanation_agent = ExplanationAgent()
user_memory = UserMemory()
rag_storage = RAGStorage()
bias_rules = BiasRulesEngine()

@app.get("/api/health")
async def health_check():
    return {"status": "FairScope is running"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), user_id: Optional[str] = None):
    try:
        if not user_id:
            user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        user_memory.store_data(user_id, df)
        tables = schema_agent.extract_tables(df)
        domain = context_agent.identify_domain(df)
        sensitive_attrs = context_agent.get_sensitive_columns(df)
        domain_sensitive = bias_rules.get_sensitive_attributes(domain)
        all_sensitive = list(set(sensitive_attrs + domain_sensitive))
        fairness_result = fairness_agent.calculate_fairness(df, all_sensitive)
        
        return JSONResponse({
            "user_id": user_id,
            "session_id": f"{user_id}_{int(pd.Timestamp.now().timestamp())}",
            "filename": file.filename,
            "domain": domain,
            "tables": tables,
            "fairness_score": float(fairness_result["score"]),
            "is_fair": fairness_result["is_fair"],
            "metrics": fairness_result["metrics"],
            "sensitive_attributes": all_sensitive,
            "target_column": fairness_result["target_column"],
            "explanation": explanation_agent.generate_explanation(fairness_result)
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/correct")
async def correct_data(data: dict):
    try:
        user_id = data.get("user_id")
        method = data.get("method")
        sensitive_attr = data.get("sensitive_attribute")
        target_col = data.get("target_column")
        
        df = user_memory.get_data(user_id)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        if method == "Reset Data (Remove Bias)":
            corrected_df = correction_agent.reset_data(df, sensitive_attr, target_col)
        elif method == "Reweight Samples":
            corrected_df = correction_agent.reweight_samples(df, sensitive_attr)
        elif method == "Resample Data":
            corrected_df = correction_agent.resample_data(df, sensitive_attr)
        else:
            corrected_df = df
        
        fairness_result = fairness_agent.calculate_fairness(corrected_df, [sensitive_attr])
        
        temp_dir = tempfile.gettempdir()
        filename = f"corrected_{user_id}.csv"
        filepath = os.path.join(temp_dir, filename)
        corrected_df.to_csv(filepath, index=False)
        
        return JSONResponse({
            "status": "success",
            "new_fairness_score": float(fairness_result["score"]),
            "is_fair": fairness_result["is_fair"],
            "explanation": f"Applied {method}. Fairness score: {fairness_result['score']:.1%}",
            "download_url": f"/api/download/{filename}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, filename=filename, media_type="text/csv")