import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.scss';
import { setupAxiosInterceptors } from './interceptors/Interceptors';

setupAxiosInterceptors(); // Инициализация перехватчиков перед запуском приложения

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
