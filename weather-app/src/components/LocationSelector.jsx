import React, { useState } from 'react';
import styled from 'styled-components';

const SelectorContainer = styled.div`
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  
  @media (min-width: 768px) {
    flex-direction: row;
    gap: 1.5rem;
  }
`;

const LocationSelect = styled.select`
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 0.8rem 1.2rem;
  font-size: 1rem;
  color: #2d3436;
  cursor: pointer;
  outline: none;
  min-width: 150px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  &:focus {
    border-color: #74b9ff;
    box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.2);
  }
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 250px;
  }
`;

const CustomInput = styled.input`
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 0.8rem 1.2rem;
  font-size: 1rem;
  color: #2d3436;
  outline: none;
  min-width: 150px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &::placeholder {
    color: #636e72;
  }
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  &:focus {
    border-color: #74b9ff;
    box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.2);
  }
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 250px;
  }
`;

const SearchButton = styled.button`
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  border: none;
  border-radius: 8px;
  padding: 0.8rem 1.5rem;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.3);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(116, 185, 255, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 250px;
  }
`;

const LocationSelector = ({ selectedLocation, onLocationChange }) => {
  const [customLocation, setCustomLocation] = useState('');
  
  // 预定义的城市列表
  const predefinedCities = [
    '北京', '上海', '广州', '深圳', '杭州', 
    '南京', '成都', '重庆', '武汉', '西安',
    '天津', '青岛', '大连', '厦门', '苏州'
  ];

  const handleSelectChange = (e) => {
    const value = e.target.value;
    if (value === 'custom') {
      // 如果选择自定义，不立即更改位置
      return;
    }
    onLocationChange(value);
  };

  const handleCustomInputChange = (e) => {
    setCustomLocation(e.target.value);
  };

  const handleCustomSearch = () => {
    if (customLocation.trim()) {
      onLocationChange(customLocation.trim());
      setCustomLocation('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleCustomSearch();
    }
  };

  return (
    <SelectorContainer>
      <LocationSelect 
        value={predefinedCities.includes(selectedLocation) ? selectedLocation : 'custom'}
        onChange={handleSelectChange}
      >
        {predefinedCities.map(city => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
        <option value="custom">自定义城市</option>
      </LocationSelect>
      
      <CustomInput
        type="text"
        placeholder="输入城市名称"
        value={customLocation}
        onChange={handleCustomInputChange}
        onKeyPress={handleKeyPress}
      />
      
      <SearchButton onClick={handleCustomSearch}>
        搜索天气
      </SearchButton>
    </SelectorContainer>
  );
};

export default LocationSelector;