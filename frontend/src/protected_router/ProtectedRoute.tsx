import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children }) => {
    const isAuthenticated = true; // Проверка авторизации
    return isAuthenticated ? children : <Navigate to='/login' />;
}