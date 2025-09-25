import React from 'react';
import styled from 'styled-components';

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  min-width: 200px;
  flex: 1;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    min-width: auto;
  }
`;

const IconContainer = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
  }
`;

const Temperature = styled.div`
  font-size: 3.5rem;
  font-weight: 300;
  color: #2d3436;
  margin-bottom: 0.5rem;
  line-height: 1;
  
  @media (max-width: 768px) {
    font-size: 2.8rem;
  }
`;

const Unit = styled.span`
  font-size: 1.5rem;
  color: #636e72;
  margin-left: 0.2rem;
`;

const Label = styled.p`
  color: #636e72;
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
  
  @media (max-width: 768px) {
    font-size: 1rem;
  }
`;

const StatusText = styled.p`
  color: #74b9ff;
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
  font-weight: 400;
`;

const TemperatureCard = ({ temperature }) => {
  // 根据温度确定状态文本和图标
  const getTemperatureStatus = (temp) => {
    if (temp <= 0) return { status: '寒冷', icon: '🥶' };
    if (temp <= 10) return { status: '偏冷', icon: '🧊' };
    if (temp <= 20) return { status: '凉爽', icon: '😊' };
    if (temp <= 30) return { status: '温暖', icon: '☀️' };
    return { status: '炎热', icon: '🔥' };
  };

  const { status, icon } = getTemperatureStatus(temperature);

  return (
    <Card>
      <IconContainer>{icon}</IconContainer>
      <Temperature>
        {Math.round(temperature)}
        <Unit>°C</Unit>
      </Temperature>
      <Label>温度</Label>
      <StatusText>{status}</StatusText>
    </Card>
  );
};

export default TemperatureCard;