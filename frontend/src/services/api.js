import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL ? `${process.env.REACT_APP_API_URL}/api` : '/api';

export const api = {
  uploadFile: async (file, userId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    const response = await axios.post(`${API_BASE_URL}/upload`, formData);
    return response.data;
  },
  
  correctData: async (userId, correctionType) => {
    const response = await axios.post(`${API_BASE_URL}/correct`, {
      user_id: userId,
      correction_type: correctionType
    });
    return response.data;
  },
  
  chatWithGemini: async (message, userId) => {
    const response = await axios.post(`${API_BASE_URL}/chat`, null, {
      params: { message, user_id: userId }
    });
    return response.data;
  },
  
  getUserHistory: async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/memory/${userId}`);
    return response.data;
  },
  
  searchSessions: async (query, nResults = 10) => {
    const response = await axios.get(`${API_BASE_URL}/search`, {
      params: { query, n_results: nResults }
    });
    return response.data;
  },
  
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  }
};