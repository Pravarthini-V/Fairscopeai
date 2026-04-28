import numpy as np
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import hashlib
import os

class RAGStorage:
    def __init__(self):
        self.storage_file = "rag_storage.json"
        self.user_data = {}
        self.session_data = {}
        self.pattern_data = {}
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_data = data.get('users', {})
                    self.session_data = data.get('sessions', {})
                    self.pattern_data = data.get('patterns', {})
            except:
                self._reset_data()
        else:
            self._reset_data()
    
    def _reset_data(self):
        """Initialize empty data structures"""
        self.user_data = {}
        self.session_data = {}
        self.pattern_data = {}
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'users': self.user_data,
                    'sessions': self.session_data,
                    'patterns': self.pattern_data
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types to Python native types"""
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(v) for v in obj]
        elif isinstance(obj, (pd.Timestamp if 'pd' in dir() else str)):
            return str(obj)
        return obj
    
    def _text_to_vector(self, text: str, size: int = 64) -> np.ndarray:
        """Convert text to vector embedding"""
        embedding = np.zeros(size)
        for i, char in enumerate(str(text)[:1000]):
            idx = ord(char) % size
            embedding[idx] += 1
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    
    def store_session(self, user_id: str, session_data: Dict) -> str:
        """Store analysis session"""
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        
        # Convert all numpy types to native Python types
        clean_data = self._convert_to_serializable(session_data)
        
        # Create text representation for embedding
        text_repr = json.dumps(clean_data, default=str)
        
        self.session_data[session_id] = {
            **clean_data,
            "user_id": str(user_id),
            "embedding": self._text_to_vector(text_repr).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
        return session_id
    
    def store_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Store user profile"""
        clean_data = self._convert_to_serializable(user_data)
        text_repr = json.dumps(clean_data, default=str)
        
        self.user_data[str(user_id)] = {
            **clean_data,
            "embedding": self._text_to_vector(text_repr).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
    
    def store_bias_pattern(self, pattern_data: Dict[str, Any]) -> str:
        """Store detected bias pattern"""
        clean_data = self._convert_to_serializable(pattern_data)
        text_repr = json.dumps(clean_data, default=str)
        
        pattern_id = f"bias_{hashlib.md5(text_repr.encode()).hexdigest()[:12]}"
        
        self.pattern_data[pattern_id] = {
            **clean_data,
            "pattern_id": pattern_id,
            "embedding": self._text_to_vector(text_repr).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
        return pattern_id
    
    def retrieve_similar_sessions(self, query: str, user_id: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Retrieve similar sessions"""
        query_embedding = self._text_to_vector(str(query))
        
        similarities = []
        for sess_id, sess_data in self.session_data.items():
            if user_id and sess_data.get('user_id') != str(user_id):
                continue
            
            sess_embedding = np.array(sess_data.get('embedding', np.zeros(64)))
            similarity = self._cosine_similarity(query_embedding, sess_embedding)
            similarities.append((similarity, sess_id, sess_data))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for sim, sess_id, sess_data in similarities[:n_results]:
            results.append({
                "session_id": sess_id,
                "metadata": sess_data,
                "similarity": float(sim)
            })
        
        return results
    
    def retrieve_similar_bias_patterns(self, domain: str, sensitive_attr: str, n_results: int = 3) -> List[Dict]:
        """Retrieve similar bias patterns"""
        query_text = f"Domain: {domain}, Attribute: {sensitive_attr}"
        query_embedding = self._text_to_vector(query_text)
        
        similarities = []
        for pat_id, pat_data in self.pattern_data.items():
            pat_embedding = np.array(pat_data.get('embedding', np.zeros(64)))
            similarity = self._cosine_similarity(query_embedding, pat_embedding)
            similarities.append((similarity, pat_id, pat_data))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for sim, pat_id, pat_data in similarities[:n_results]:
            results.append({
                "pattern_id": pat_id,
                "metadata": pat_data,
                "similarity": float(sim)
            })
        
        return results
    
    def update_user_fairness_history(self, user_id: str, fairness_result: Dict[str, Any]):
        """Update user's fairness history"""
        user_id = str(user_id)
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "embedding": [],
                "fairness_history": []
            }
        
        if 'fairness_history' not in self.user_data[user_id]:
            self.user_data[user_id]['fairness_history'] = []
        
        # Convert numpy values
        history_entry = {
            "score": float(fairness_result.get('score', 0)),
            "is_fair": bool(fairness_result.get('is_fair', False)),
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_data[user_id]['fairness_history'].append(history_entry)
        self.save_data()
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's analysis history"""
        user_sessions = []
        for sess_id, sess_data in self.session_data.items():
            if sess_data.get('user_id') == str(user_id):
                user_sessions.append({
                    "session_id": sess_id,
                    "metadata": sess_data
                })
        
        user_sessions.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)
        return user_sessions[:limit]