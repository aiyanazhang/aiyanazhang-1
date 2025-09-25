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

const Humidity = styled.div`
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

const ProgressBar = styled.div`
  width: 100%;
  height: 6px;
  background-color: #ddd;
  border-radius: 3px;
  margin: 1rem 0 0.5rem 0;
  overflow: hidden;
`;

const Progress = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #74b9ff 0%, #0984e3 100%);
  border-radius: 3px;
  width: ${props => props.percentage}%;
  transition: width 0.3s ease;
`;

const HumidityCard = ({ humidity }) => {
  // 根据湿度确定状态文本和图标
  const getHumidityStatus = (humid) => {
    if (humid <= 30) return { status: '干燥', icon: '🏜️' };
    if (humid <= 60) return { status: '舒适', icon: '😌' };
    if (humid <= 80) return { status: '湿润', icon: '💧' };
    return { status: '潮湿', icon: '🌧️' };
  };

  const { status, icon } = getHumidityStatus(humidity);

  return (
    <Card>
      <IconContainer>{icon}</IconContainer>
      <Humidity>
        {Math.round(humidity)}
        <Unit>%</Unit>
      </Humidity>
      <Label>湿度</Label>
      <ProgressBar>
        <Progress percentage={humidity} />
      </ProgressBar>
      <StatusText>{status}</StatusText>
    </Card>
  );
};

export default HumidityCard;