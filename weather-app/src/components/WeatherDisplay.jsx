import React from 'react';
import styled from 'styled-components';
import TemperatureCard from './TemperatureCard';
import HumidityCard from './HumidityCard';

const DisplayContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 800px;
  width: 100%;
  
  @media (min-width: 768px) {
    flex-direction: row;
    justify-content: center;
    align-items: stretch;
  }
`;

const LocationInfo = styled.div`
  text-align: center;
  margin-bottom: 1.5rem;
`;

const LocationText = styled.h2`
  color: white;
  font-size: 1.5rem;
  font-weight: 400;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    font-size: 1.3rem;
  }
`;

const LastUpdated = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
`;

const WeatherDisplay = ({ weatherData }) => {
  if (!weatherData) {
    return null;
  }

  const { temperature, humidity, location, lastUpdated } = weatherData;
  
  // 格式化最后更新时间
  const formatLastUpdated = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      <LocationInfo>
        <LocationText>{location}</LocationText>
        <LastUpdated>
          最后更新: {formatLastUpdated(lastUpdated)}
        </LastUpdated>
      </LocationInfo>
      
      <DisplayContainer>
        <TemperatureCard temperature={temperature} />
        <HumidityCard humidity={humidity} />
      </DisplayContainer>
    </>
  );
};

export default WeatherDisplay;