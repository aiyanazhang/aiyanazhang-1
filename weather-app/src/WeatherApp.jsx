import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import WeatherDisplay from './components/WeatherDisplay';
import LocationSelector from './components/LocationSelector';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import { getCurrentWeather } from './services/weatherService';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const Title = styled.h1`
  color: white;
  font-size: 2.5rem;
  font-weight: 300;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  
  @media (max-width: 768px) {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }
`;

const WeatherApp = () => {
  // 状态管理
  const [weatherData, setWeatherData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState('北京');

  // 获取天气数据的函数
  const fetchWeatherData = useCallback(async (location) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await getCurrentWeather(location);
      setWeatherData({
        temperature: data.temperature,
        humidity: data.humidity,
        location: data.location,
        lastUpdated: new Date().getTime()
      });
    } catch (err) {
      setError(err.message || '获取天气信息失败，请稍后重试');
      console.error('获取天气数据失败:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 组件挂载时获取天气数据
  useEffect(() => {
    fetchWeatherData(selectedLocation);
  }, [selectedLocation, fetchWeatherData]);

  // 位置变更处理
  const handleLocationChange = useCallback((newLocation) => {
    setSelectedLocation(newLocation);
  }, []);

  // 重试处理
  const handleRetry = useCallback(() => {
    fetchWeatherData(selectedLocation);
  }, [fetchWeatherData, selectedLocation]);

  return (
    <AppContainer>
      <Title>天气信息</Title>
      
      <LocationSelector 
        selectedLocation={selectedLocation}
        onLocationChange={handleLocationChange}
      />
      
      {isLoading && <LoadingSpinner />}
      
      {error && (
        <ErrorMessage 
          error={error}
          onRetry={handleRetry}
        />
      )}
      
      {!isLoading && !error && weatherData && (
        <WeatherDisplay weatherData={weatherData} />
      )}
    </AppContainer>
  );
};

export default WeatherApp;