// ==============================================================================
// VÙNG DÙNG CHUNG (VÙNG CẤM) - frontend/src/lib/api.ts
// Cấu hình Axios Client giao tiếp với FastAPI Backend.
// Bắt buộc qua PR có xét duyệt của Mentor / Tech Lead.
// ==============================================================================

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: tự động đính kèm Bearer Token nếu có
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: xử lý lỗi toàn cục
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token hết hạn hoặc không hợp lệ -> xóa token và chuyển về login nếu đang ở admin
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      if (window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
