# rag_storage.py - Without sentence-transformers
import numpy as np
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import hashlib
import os

class RAGStorage:
    def __init__(self):
        # Simple TF-IDF style embedding (no PyTorch needed)
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
                self.user_data = {}
                self.session_data = {}
                self.pattern_data = {}
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump({
                'users': self.user_data,
                'sessions': self.session_data,
                'patterns': self.pattern_data
            }, f, indent=2)
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Create simple embedding using character frequencies (no PyTorch)"""
        # Simple hash-based embedding
        embedding = np.zeros(64)
        for i, char in enumerate(text[:1000]):
            idx = ord(char) % 64
            embedding[idx] += 1
        # Normalize
        if np.linalg.norm(embedding) > 0:
            embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
    
    def store_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Store user profile"""
        self.user_data[user_id] = {
            **user_data,
            "embedding": self._simple_embedding(json.dumps(user_data)).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
    
    def store_session(self, user_id: str, session_data: Dict) -> str:
        """Store session data"""
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        
        self.session_data[session_id] = {
            **session_data,
            "user_id": user_id,
            "embedding": self._simple_embedding(json.dumps(session_data)).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
        
        return session_id
    
    def retrieve_similar_sessions(self, query: str, user_id: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Retrieve similar sessions using simple similarity"""
        query_embedding = self._simple_embedding(query)
        
        similarities = []
        for sess_id, sess_data in self.session_data.items():
            if user_id and sess_data.get('user_id') != user_id:
                continue
            
            sess_embedding = np.array(sess_data.get('embedding', np.zeros(64)))
            similarity = self._cosine_similarity(query_embedding, sess_embedding)
            similarities.append((similarity, sess_id, sess_data))
        
        # Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for sim, sess_id, sess_data in similarities[:n_results]:
            results.append({
                "document": json.dumps(sess_data),
                "metadata": sess_data,
                "similarity": float(sim),
                "session_id": sess_id
            })
        
        return results
    
    def get_user_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user's historical sessions"""
        history = []
        for sess_id, sess_data in self.session_data.items():
            if sess_data.get('user_id') == user_id:
                history.append({
                    "session_data": json.dumps(sess_data),
                    "metadata": sess_data,
                    "session_id": sess_id
                })
        
        # Sort by timestamp
        history.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)
        return history[:limit]
    
    def store_bias_pattern(self, pattern_data: Dict[str, Any]):
        """Store bias pattern"""
        pattern_id = f"pattern_{hashlib.md5(json.dumps(pattern_data).encode()).hexdigest()[:16]}"
        
        self.pattern_data[pattern_id] = {
            **pattern_data,
            "embedding": self._simple_embedding(json.dumps(pattern_data)).tolist(),
            "timestamp": datetime.now().isoformat()
        }
        self.save_data()
        
        return pattern_id
    
    def retrieve_similar_bias_patterns(self, domain: str, sensitive_attr: str, n_results: int = 3) -> List[Dict]:
        """Retrieve similar bias patterns"""
        query_text = f"Domain: {domain}, Sensitive Attribute: {sensitive_attr}"
        query_embedding = self._simple_embedding(query_text)
        
        similarities = []
        for pat_id, pat_data in self.pattern_data.items():
            pat_embedding = np.array(pat_data.get('embedding', np.zeros(64)))
            similarity = self._cosine_similarity(query_embedding, pat_embedding)
            similarities.append((similarity, pat_id, pat_data))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for sim, pat_id, pat_data in similarities[:n_results]:
            results.append({
                "pattern": json.dumps(pat_data),
                "metadata": pat_data,
                "similarity": float(sim)
            })
        
        return results
    
    def update_user_fairness_history(self, user_id: str, fairness_result: Dict[str, Any]):
        """Update user's fairness history"""
        if user_id in self.user_data:
            if 'fairness_history' not in self.user_data[user_id]:
                self.user_data[user_id]['fairness_history'] = []
            
            self.user_data[user_id]['fairness_history'].append({
                "score": fairness_result.get('score', 0),
                "is_fair": fairness_result.get('is_fair', False),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update embedding
            self.user_data[user_id]['embedding'] = self._simple_embedding(
                json.dumps(self.user_data[user_id])
            ).tolist()
            self.save_data()
    
    def semantic_search_sessions(self, search_text: str, n_results: int = 10) -> List[Dict]:
        """General semantic search across sessions"""
        return self.retrieve_similar_sessions(search_text, n_results=n_results)
    
    def get_similar_users(self, user_profile: Dict[str, Any], n_results: int = 5) -> List[Dict]:
        """Find similar users"""
        query_text = f"Domain: {user_profile.get('domain', 'unknown')}"
        query_embedding = self._simple_embedding(query_text)
        
        similarities = []
        for uid, udata in self.user_data.items():
            if uid == user_profile.get('user_id'):
                continue
            
            u_embedding = np.array(udata.get('embedding', np.zeros(64)))
            similarity = self._cosine_similarity(query_embedding, u_embedding)
            similarities.append((similarity, uid, udata))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        results = []
        for sim, uid, udata in similarities[:n_results]:
            results.append({
                "user_id": uid,
                "metadata": udata,
                "similarity": float(sim)
            })
        
        return results