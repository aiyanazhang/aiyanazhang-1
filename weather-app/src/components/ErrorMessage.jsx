import React from 'react';
import styled from 'styled-components';

const ErrorContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  max-width: 400px;
  width: 100%;
  margin: 2rem 0;
  border-left: 4px solid #e74c3c;
`;

const ErrorIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const ErrorTitle = styled.h3`
  color: #e74c3c;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
`;

const ErrorText = styled.p`
  color: #636e72;
  font-size: 1rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
`;

const RetryButton = styled.button`
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  border: none;
  border-radius: 8px;
  padding: 0.8rem 2rem;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ErrorMessage = ({ error, onRetry }) => {
  if (!error) return null;

  return (
    <ErrorContainer>
      <ErrorIcon>⚠️</ErrorIcon>
      <ErrorTitle>获取天气信息失败</ErrorTitle>
      <ErrorText>{error}</ErrorText>
      {onRetry && (
        <RetryButton onClick={onRetry}>
          重试
        </RetryButton>
      )}
    </ErrorContainer>
  );
};

export default ErrorMessage;