/**
 * 应用配置文件
 * 包含API配置、默认设置和常量定义
 */

window.WeatherConfig = {
    // API配置
    API: {
        // 和风天气API配置 (推荐用于中国地区)
        QWEATHER: {
            BASE_URL: 'https://devapi.qweather.com/v7',
            KEY: 'YOUR_QWEATHER_API_KEY', // 需要替换为实际的API密钥
            LOCATION_ID: '101010300', // 北京朝阳区的位置ID
            ENDPOINTS: {
                CURRENT: '/weather/now',
                LOCATION: '/city/lookup'
            }
        },
        
        // OpenWeatherMap API配置 (备用)
        OPENWEATHER: {
            BASE_URL: 'https://api.openweathermap.org/data/2.5',
            KEY: 'YOUR_OPENWEATHER_API_KEY', // 需要替换为实际的API密钥
            LOCATION: {
                lat: 39.9211,  // 北京朝阳区纬度
                lon: 116.4439  // 北京朝阳区经度
            },
            ENDPOINTS: {
                CURRENT: '/weather'
            }
        },
        
        // 当前使用的API提供商
        PROVIDER: 'DEMO', // 'QWEATHER', 'OPENWEATHER', 'DEMO'
        
        // 请求配置
        TIMEOUT: 10000, // 10秒超时
        RETRY_TIMES: 3, // 重试次数
        RETRY_DELAY: 1000 // 重试延迟(毫秒)
    },

    // 缓存配置
    CACHE: {
        // 缓存键名
        KEYS: {
            WEATHER_DATA: 'weather_data',
            LAST_UPDATE: 'last_update',
            BACKUP_DATA: 'backup_weather_data'
        },
        
        // 缓存有效期 (毫秒)
        EXPIRY: {
            WEATHER_DATA: 30 * 60 * 1000, // 30分钟
            BACKUP_DATA: 24 * 60 * 60 * 1000 // 24小时
        }
    },

    // UI配置
    UI: {
        // 自动刷新间隔 (毫秒)
        AUTO_REFRESH_INTERVAL: 10 * 60 * 1000, // 10分钟
        
        // 动画持续时间 (毫秒)
        ANIMATION_DURATION: 300,
        
        // 加载延迟显示时间 (毫秒)
        LOADING_DELAY: 500,
        
        // 时间格式
        TIME_FORMAT: {
            DISPLAY: 'YYYY-MM-DD HH:mm:ss',
            API: 'YYYY-MM-DDTHH:mm:ssZ'
        }
    },

    // 地理位置配置
    LOCATION: {
        DEFAULT: {
            name: '北京市朝阳区',
            coordinates: {
                latitude: 39.9211,
                longitude: 116.4439
            },
            timezone: 'Asia/Shanghai'
        }
    },

    // 天气图标映射
    WEATHER_ICONS: {
        // 和风天气图标代码映射
        QWEATHER: {
            '100': 'sunny.png',           // 晴
            '101': 'cloudy.png',          // 多云
            '102': 'few-clouds.png',      // 少云
            '103': 'partly-cloudy.png',   // 晴间多云
            '104': 'overcast.png',        // 阴
            '150': 'clear-night.png',     // 晴(夜间)
            '151': 'cloudy-night.png',    // 多云(夜间)
            '152': 'few-clouds-night.png', // 少云(夜间)
            '153': 'partly-cloudy-night.png', // 晴间多云(夜间)
            '300': 'shower-rain.png',     // 阵雨
            '301': 'heavy-shower-rain.png', // 强阵雨
            '302': 'thunderstorm.png',    // 雷阵雨
            '303': 'heavy-thunderstorm.png', // 强雷阵雨
            '304': 'thunderstorm-with-hail.png', // 雷阵雨伴有冰雹
            '305': 'light-rain.png',      // 小雨
            '306': 'moderate-rain.png',   // 中雨
            '307': 'heavy-rain.png',      // 大雨
            '308': 'extreme-rain.png',    // 极端降雨
            '309': 'drizzle.png',         // 毛毛雨/细雨
            '310': 'heavy-storm.png',     // 暴雨
            '311': 'severe-storm.png',    // 大暴雨
            '312': 'extreme-storm.png',   // 特大暴雨
            '313': 'freezing-rain.png',   // 冻雨
            '400': 'light-snow.png',      // 小雪
            '401': 'moderate-snow.png',   // 中雪
            '402': 'heavy-snow.png',      // 大雪
            '403': 'snowstorm.png',       // 暴雪
            '404': 'sleet.png',           // 雨夹雪
            '405': 'rain-and-snow.png',   // 雨雪天气
            '406': 'shower-snow.png',     // 阵雪
            '407': 'snow-flurry.png',     // 阵雪
            '408': 'light-to-moderate-snow.png', // 小到中雪
            '409': 'moderate-to-heavy-snow.png', // 中到大雪
            '410': 'heavy-snow-to-snowstorm.png', // 大到暴雪
            '500': 'mist.png',            // 薄雾
            '501': 'fog.png',             // 雾
            '502': 'haze.png',            // 霾
            '503': 'sand.png',            // 扬沙
            '504': 'dust.png',            // 浮尘
            '507': 'duststorm.png',       // 沙尘暴
            '508': 'sandstorm.png',       // 强沙尘暴
            '509': 'dense-fog.png',       // 浓雾
            '510': 'severe-haze.png',     // 强浓雾
            '511': 'moderate-haze.png',   // 中度霾
            '512': 'heavy-haze.png',      // 重度霾
            '513': 'severe-haze.png',     // 严重霾
            '514': 'heavy-fog.png',       // 大雾
            '515': 'extra-heavy-fog.png', // 特强浓雾
            '900': 'hot.png',             // 热
            '901': 'cold.png',            // 冷
            '999': 'unknown.png'          // 未知
        },
        
        // 默认图标路径
        BASE_PATH: 'src/images/weather-icons/',
        DEFAULT_ICON: 'unknown.png'
    },

    // 单位配置
    UNITS: {
        TEMPERATURE: '°C',
        WIND_SPEED: 'km/h',
        PRESSURE: 'hPa',
        VISIBILITY: 'km',
        HUMIDITY: '%'
    },

    // 错误消息配置
    ERROR_MESSAGES: {
        NETWORK_ERROR: '网络连接失败，请检查网络设置',
        API_ERROR: '天气数据获取失败，请稍后重试',
        TIMEOUT_ERROR: '请求超时，请检查网络连接',
        INVALID_DATA: '天气数据格式错误',
        CACHE_ERROR: '缓存操作失败',
        UNKNOWN_ERROR: '发生未知错误，请刷新页面重试'
    },

    // 调试配置
    DEBUG: {
        ENABLED: true, // 开发环境开启，生产环境关闭
        LOG_LEVEL: 'info', // 'error', 'warn', 'info', 'debug'
        SHOW_CACHE_INFO: true,
        SHOW_API_REQUESTS: true
    },

    // 演示数据 (用于开发和展示)
    DEMO_DATA: {
        location: '北京市朝阳区',
        temperature: 25,
        feelsLike: 27,
        condition: '晴',
        conditionCode: '100',
        humidity: 65,
        windSpeed: 12,
        windDirection: '东南风',
        pressure: 1013,
        visibility: 10,
        updateTime: new Date().toISOString(),
        iconCode: '100'
    }
};

// 环境检测和配置调整
(function() {
    // 检测是否为生产环境
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        WeatherConfig.DEBUG.ENABLED = false;
        WeatherConfig.DEBUG.LOG_LEVEL = 'error';
    }
    
    // 检测是否支持localStorage
    try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
    } catch (e) {
        console.warn('localStorage不可用，将使用内存缓存');
        WeatherConfig.CACHE.USE_MEMORY = true;
    }
    
    // 冻结配置对象，防止意外修改
    Object.freeze(WeatherConfig);
})();