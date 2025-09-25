import '@testing-library/jest-dom';

// Mock styled-components globally
jest.mock('styled-components', () => {
  const React = require('react');
  return {
    __esModule: true,
    default: (tag) => (props) => React.createElement(tag, props),
    keyframes: () => '',
  };
});

// Global test setup
global.console = {
  ...console,
  // 静默一些测试中的日志
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};