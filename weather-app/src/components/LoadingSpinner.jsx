import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
`;

const Spinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: 1.5rem;
`;

const LoadingText = styled.p`
  color: white;
  font-size: 1.1rem;
  font-weight: 300;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
`;

const LoadingSpinner = ({ isLoading = true }) => {
  if (!isLoading) return null;

  return (
    <SpinnerContainer>
      <Spinner />
      <LoadingText>正在获取天气信息...</LoadingText>
    </SpinnerContainer>
  );
};

export default LoadingSpinner;