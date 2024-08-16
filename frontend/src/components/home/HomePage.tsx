import React from 'react';
import './HomePage.scss';
import Header from '../header/Header';

const HomePage: React.FC = () => {

  return (
    // Верстка домашней страницы
      <div>
          <Header />
          <div className={'home'}>
              <h1>ONLINE STORE PRO</h1>
              <p>Лучшая админ панель на React App!</p>
          </div>
      </div>
  );
}

export default HomePage;
