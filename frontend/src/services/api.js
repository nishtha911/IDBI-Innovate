import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // Assuming standard FastAPI local port
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for global error handling (optional, but good practice)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
