import axios from 'axios';

// 模拟天气数据
const mockWeatherData = {
  '北京': { temperature: 15, humidity: 45, location: '北京' },
  '上海': { temperature: 22, humidity: 65, location: '上海' },
  '广州': { temperature: 28, humidity: 75, location: '广州' },
  '深圳': { temperature: 26, humidity: 70, location: '深圳' },
  '杭州': { temperature: 20, humidity: 60, location: '杭州' },
  '南京': { temperature: 18, humidity: 55, location: '南京' },
  '成都': { temperature: 16, humidity: 80, location: '成都' },
  '重庆': { temperature: 19, humidity: 75, location: '重庆' },
  '武汉': { temperature: 17, humidity: 65, location: '武汉' },
  '西安': { temperature: 14, humidity: 50, location: '西安' },
  '天津': { temperature: 13, humidity: 48, location: '天津' },
  '青岛': { temperature: 16, humidity: 62, location: '青岛' },
  '大连': { temperature: 12, humidity: 58, location: '大连' },
  '厦门': { temperature: 24, humidity: 72, location: '厦门' },
  '苏州': { temperature: 21, humidity: 58, location: '苏州' }
};

// 配置信息
const API_CONFIG = {
  // OpenWeatherMap API配置（示例）
  BASE_URL: 'https://api.openweathermap.org/data/2.5',
  API_KEY: process.env.REACT_APP_WEATHER_API_KEY || 'demo_key',
  
  // 请求超时时间
  TIMEOUT: 10000,
  
  // 缓存时间（毫秒）
  CACHE_DURATION: 5 * 60 * 1000, // 5分钟
};

// 内存缓存
const cache = new Map();

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发起天气API请求:', config.url);
    return config;
  },
  (error) => {
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('天气API响应成功:', response.status);
    return response;
  },
  (error) => {
    console.error('天气API响应错误:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// 生成缓存键
const getCacheKey = (location, units = 'metric') => {
  return `weather_${location}_${units}`;
};

// 检查缓存是否有效
const isCacheValid = (cachedData) => {
  if (!cachedData) return false;
  return Date.now() - cachedData.timestamp < API_CONFIG.CACHE_DURATION;
};

// 模拟API延迟
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 生成随机天气数据（用于未预定义的城市）
const generateRandomWeatherData = (location) => {
  const baseTemp = Math.random() * 40 - 10; // -10°C 到 30°C
  const baseHumidity = Math.random() * 60 + 20; // 20% 到 80%
  
  return {
    temperature: Math.round(baseTemp * 10) / 10, // 保留一位小数
    humidity: Math.round(baseHumidity),
    location: location
  };
};

// 获取当前天气信息
export const getCurrentWeather = async (location, units = 'metric') => {
  try {
    // 检查缓存
    const cacheKey = getCacheKey(location, units);
    const cachedData = cache.get(cacheKey);
    
    if (isCacheValid(cachedData)) {
      console.log('使用缓存的天气数据:', location);
      return cachedData.data;
    }

    // 模拟网络延迟
    await delay(800 + Math.random() * 1200); // 0.8-2秒随机延迟

    // 检查是否需要使用真实API
    const useRealAPI = API_CONFIG.API_KEY && API_CONFIG.API_KEY !== 'demo_key';
    
    let weatherData;
    
    if (useRealAPI) {
      // 真实API调用
      try {
        const response = await apiClient.get('/weather', {
          params: {
            q: location,
            appid: API_CONFIG.API_KEY,
            units: units,
            lang: 'zh_cn'
          }
        });

        const data = response.data;
        weatherData = {
          temperature: data.main.temp,
          humidity: data.main.humidity,
          location: data.name
        };
      } catch (apiError) {
        console.warn('真实API调用失败，使用模拟数据:', apiError.message);
        throw new Error('网络连接异常，请检查网络设置');
      }
    } else {
      // 使用模拟数据
      console.log('使用模拟天气数据:', location);
      
      // 检查是否为预定义城市
      if (mockWeatherData[location]) {
        weatherData = { ...mockWeatherData[location] };
      } else {
        // 生成随机数据
        weatherData = generateRandomWeatherData(location);
      }
      
      // 随机模拟一些错误情况（10%概率）
      if (Math.random() < 0.1) {
        throw new Error('服务器暂时无法获取该城市的天气信息');
      }
    }

    // 存储到缓存
    cache.set(cacheKey, {
      data: weatherData,
      timestamp: Date.now()
    });

    return weatherData;

  } catch (error) {
    // 错误处理
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请检查网络连接');
    }
    
    if (error.response) {
      const status = error.response.status;
      switch (status) {
        case 401:
          throw new Error('API密钥无效');
        case 404:
          throw new Error('未找到该城市的天气信息');
        case 429:
          throw new Error('请求过于频繁，请稍后重试');
        case 500:
          throw new Error('服务器错误，请稍后重试');
        default:
          throw new Error(`服务器错误 (${status})`);
      }
    }
    
    // 如果是我们自定义的错误，直接抛出
    if (error.message.includes('服务器暂时无法获取') || 
        error.message.includes('网络连接异常')) {
      throw error;
    }
    
    // 默认错误
    throw new Error('获取天气信息失败，请稍后重试');
  }
};

// 清除缓存
export const clearWeatherCache = () => {
  cache.clear();
  console.log('天气数据缓存已清除');
};

// 获取缓存统计信息
export const getCacheStats = () => {
  return {
    size: cache.size,
    keys: Array.from(cache.keys())
  };
};