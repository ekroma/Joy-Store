import React from 'react';
import './Button.scss'

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  type?: 'button' | 'submit' | 'reset';
  buttonType?: 'login' | 'other';
}

const Button: React.FC<ButtonProps> = ({ children, onClick, type, buttonType}) => {
  return (
    <>
      {buttonType === 'login' ? (
        // Верстка для кнопки входа
        <button type={type} onClick={onClick} className="loginButton">
          {children}
        </button>
      ) : (
        // Верстка для других типов кнопок
        <button type={buttonType} onClick={onClick} className="otherButton">
          {children}
        </button>
      )}
    </>
  );
};

export default Button;
