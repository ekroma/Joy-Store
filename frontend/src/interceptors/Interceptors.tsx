// Interceptors.tsx
import axios from 'axios';

export const setupAxiosInterceptors = () => {
  axios.interceptors.response.use(response => response, error => {
    if (error.response && error.response.status === 418) {
      // Перенаправление на страницу входа
      window.location.href = '/login';
    }
    return Promise.reject(error);
  });
};
