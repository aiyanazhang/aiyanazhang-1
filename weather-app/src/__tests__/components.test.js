import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TemperatureCard from '../components/TemperatureCard';
import HumidityCard from '../components/HumidityCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

// Mock styled-components
jest.mock('styled-components', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: (tag) => (props) => React.createElement(tag, props),
    keyframes: () => '',
  };
});

describe('WeatherComponents', () => {
  describe('TemperatureCard', () => {
    it('应该正确显示温度信息', () => {
      render(<TemperatureCard temperature={25} />);
      
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('°C')).toBeInTheDocument();
      expect(screen.getByText('温度')).toBeInTheDocument();
      expect(screen.getByText('温暖')).toBeInTheDocument();
    });

    it('应该根据温度显示正确的状态', () => {
      const testCases = [
        { temp: -5, expectedStatus: '寒冷', expectedIcon: '🥶' },
        { temp: 5, expectedStatus: '偏冷', expectedIcon: '🧊' },
        { temp: 15, expectedStatus: '凉爽', expectedIcon: '😊' },
        { temp: 25, expectedStatus: '温暖', expectedIcon: '☀️' },
        { temp: 35, expectedStatus: '炎热', expectedIcon: '🔥' }
      ];

      testCases.forEach(({ temp, expectedStatus, expectedIcon }) => {
        const { rerender } = render(<TemperatureCard temperature={temp} />);
        
        expect(screen.getByText(expectedStatus)).toBeInTheDocument();
        expect(screen.getByText(expectedIcon)).toBeInTheDocument();
        
        rerender(<div />); // 清除组件
      });
    });

    it('应该四舍五入显示温度', () => {
      render(<TemperatureCard temperature={25.7} />);
      expect(screen.getByText('26')).toBeInTheDocument();
      
      const { rerender } = render(<TemperatureCard temperature={25.7} />);
      rerender(<TemperatureCard temperature={25.3} />);
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });

  describe('HumidityCard', () => {
    it('应该正确显示湿度信息', () => {
      render(<HumidityCard humidity={65} />);
      
      expect(screen.getByText('65')).toBeInTheDocument();
      expect(screen.getByText('%')).toBeInTheDocument();
      expect(screen.getByText('湿度')).toBeInTheDocument();
      expect(screen.getByText('湿润')).toBeInTheDocument();
    });

    it('应该根据湿度显示正确的状态', () => {
      const testCases = [
        { humidity: 25, expectedStatus: '干燥', expectedIcon: '🏜️' },
        { humidity: 45, expectedStatus: '舒适', expectedIcon: '😌' },
        { humidity: 70, expectedStatus: '湿润', expectedIcon: '💧' },
        { humidity: 85, expectedStatus: '潮湿', expectedIcon: '🌧️' }
      ];

      testCases.forEach(({ humidity, expectedStatus, expectedIcon }) => {
        const { rerender } = render(<HumidityCard humidity={humidity} />);
        
        expect(screen.getByText(expectedStatus)).toBeInTheDocument();
        expect(screen.getByText(expectedIcon)).toBeInTheDocument();
        
        rerender(<div />); // 清除组件
      });
    });

    it('应该四舍五入显示湿度', () => {
      render(<HumidityCard humidity={65.7} />);
      expect(screen.getByText('66')).toBeInTheDocument();
      
      const { rerender } = render(<HumidityCard humidity={65.7} />);
      rerender(<HumidityCard humidity={65.3} />);
      expect(screen.getByText('65')).toBeInTheDocument();
    });
  });

  describe('LoadingSpinner', () => {
    it('应该在加载时显示加载信息', () => {
      render(<LoadingSpinner isLoading={true} />);
      
      expect(screen.getByText('正在获取天气信息...')).toBeInTheDocument();
    });

    it('应该在不加载时不显示', () => {
      render(<LoadingSpinner isLoading={false} />);
      
      expect(screen.queryByText('正在获取天气信息...')).not.toBeInTheDocument();
    });

    it('默认应该显示加载状态', () => {
      render(<LoadingSpinner />);
      
      expect(screen.getByText('正在获取天气信息...')).toBeInTheDocument();
    });
  });

  describe('ErrorMessage', () => {
    const mockRetry = jest.fn();

    beforeEach(() => {
      mockRetry.mockClear();
    });

    it('应该显示错误信息', () => {
      const errorText = '网络连接失败';
      render(<ErrorMessage error={errorText} onRetry={mockRetry} />);
      
      expect(screen.getByText('获取天气信息失败')).toBeInTheDocument();
      expect(screen.getByText(errorText)).toBeInTheDocument();
      expect(screen.getByText('重试')).toBeInTheDocument();
    });

    it('应该在没有错误时不显示', () => {
      render(<ErrorMessage error={null} onRetry={mockRetry} />);
      
      expect(screen.queryByText('获取天气信息失败')).not.toBeInTheDocument();
    });

    it('应该在点击重试按钮时调用onRetry', () => {
      render(<ErrorMessage error="测试错误" onRetry={mockRetry} />);
      
      const retryButton = screen.getByText('重试');
      fireEvent.click(retryButton);
      
      expect(mockRetry).toHaveBeenCalledTimes(1);
    });

    it('应该在没有onRetry时不显示重试按钮', () => {
      render(<ErrorMessage error="测试错误" />);
      
      expect(screen.queryByText('重试')).not.toBeInTheDocument();
    });
  });
});