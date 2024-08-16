import React from 'react';
import axios from 'axios';

export const getUserProfile = async () => {
  try {
    const response = await axios.get('http://localhost:8000/online_store/v1/auth/get-user-profile', {
      withCredentials: true});
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении профиля пользователя:', error);
    return null;
  }
};

