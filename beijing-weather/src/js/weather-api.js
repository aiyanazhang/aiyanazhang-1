/**
 * 天气API服务
 * 负责与天气API的交互和数据处理
 */

window.WeatherAPI = {
    
    /**
     * 获取天气数据的主入口
     * @returns {Promise<Object>} 天气数据
     */
    async getWeatherData() {
        WeatherUtils.Logger.info('开始获取天气数据');
        
        try {
            // 根据配置选择API提供商
            switch (WeatherConfig.API.PROVIDER) {
                case 'QWEATHER':
                    return await this.getQWeatherData();
                case 'OPENWEATHER':
                    return await this.getOpenWeatherData();
                case 'DEMO':
                default:
                    return await this.getDemoData();
            }
        } catch (error) {
            WeatherUtils.Logger.error('获取天气数据失败', error);
            throw error;
        }
    },
    
    /**
     * 获取和风天气数据
     * @returns {Promise<Object>} 处理后的天气数据
     */
    async getQWeatherData() {
        const config = WeatherConfig.API.QWEATHER;
        const url = `${config.BASE_URL}${config.ENDPOINTS.CURRENT}?location=${config.LOCATION_ID}&key=${config.KEY}`;
        
        try {
            const response = await WeatherUtils.Network.retry(
                () => WeatherUtils.Network.request(url)
            );
            
            if (response.code !== '200') {
                throw new Error(`和风天气API错误: ${response.code}`);
            }
            
            return this.transformQWeatherData(response.now);
        } catch (error) {
            WeatherUtils.Logger.error('和风天气API请求失败', error);
            throw new Error('获取和风天气数据失败: ' + error.message);
        }
    },
    
    /**
     * 获取OpenWeatherMap数据
     * @returns {Promise<Object>} 处理后的天气数据
     */
    async getOpenWeatherData() {
        const config = WeatherConfig.API.OPENWEATHER;
        const url = `${config.BASE_URL}${config.ENDPOINTS.CURRENT}?lat=${config.LOCATION.lat}&lon=${config.LOCATION.lon}&appid=${config.KEY}&units=metric&lang=zh_cn`;
        
        try {
            const response = await WeatherUtils.Network.retry(
                () => WeatherUtils.Network.request(url)
            );
            
            return this.transformOpenWeatherData(response);
        } catch (error) {
            WeatherUtils.Logger.error('OpenWeatherMap API请求失败', error);
            throw new Error('获取OpenWeatherMap数据失败: ' + error.message);
        }
    },
    
    /**
     * 获取演示数据 (用于开发和展示)
     * @returns {Promise<Object>} 演示天气数据
     */
    async getDemoData() {
        WeatherUtils.Logger.info('使用演示数据');
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 生成一些随机变化的演示数据
        const baseData = WeatherConfig.DEMO_DATA;
        const randomVariation = () => Math.floor(Math.random() * 10) - 5; // -5 到 +5
        
        return {
            ...baseData,
            temperature: baseData.temperature + randomVariation(),
            humidity: Math.max(0, Math.min(100, baseData.humidity + randomVariation())),
            windSpeed: Math.max(0, baseData.windSpeed + randomVariation()),
            pressure: baseData.pressure + randomVariation(),
            updateTime: new Date().toISOString()
        };
    },
    
    /**
     * 转换和风天气数据格式
     * @param {Object} data 和风天气原始数据
     * @returns {Object} 标准化的天气数据
     */
    transformQWeatherData(data) {
        WeatherUtils.Logger.debug('转换和风天气数据', data);
        
        return {
            location: WeatherConfig.LOCATION.DEFAULT.name,
            temperature: WeatherUtils.Validator.sanitizeTemperature(data.temp),
            feelsLike: WeatherUtils.Validator.sanitizeTemperature(data.feelsLike),
            condition: this.getWeatherCondition(data.text),
            conditionCode: data.icon,
            humidity: WeatherUtils.Validator.sanitizeHumidity(data.humidity),
            windSpeed: this.convertWindSpeed(data.windSpeed, data.windScale),
            windDirection: this.getWindDirection(data.windDir, data.wind360),
            pressure: this.sanitizePressure(data.pressure),
            visibility: this.sanitizeVisibility(data.vis),
            updateTime: data.obsTime,
            iconCode: data.icon
        };
    },
    
    /**
     * 转换OpenWeatherMap数据格式
     * @param {Object} data OpenWeatherMap原始数据
     * @returns {Object} 标准化的天气数据
     */
    transformOpenWeatherData(data) {
        WeatherUtils.Logger.debug('转换OpenWeatherMap数据', data);
        
        const weather = data.weather[0];
        const main = data.main;
        const wind = data.wind || {};
        
        return {
            location: WeatherConfig.LOCATION.DEFAULT.name,
            temperature: WeatherUtils.Validator.sanitizeTemperature(main.temp),
            feelsLike: WeatherUtils.Validator.sanitizeTemperature(main.feels_like),
            condition: weather.description,
            conditionCode: weather.icon,
            humidity: WeatherUtils.Validator.sanitizeHumidity(main.humidity),
            windSpeed: this.convertWindSpeedFromMps(wind.speed),
            windDirection: this.getWindDirectionFromDegrees(wind.deg),
            pressure: this.sanitizePressure(main.pressure),
            visibility: this.sanitizeVisibility(data.visibility / 1000), // 转换为km
            updateTime: new Date(data.dt * 1000).toISOString(),
            iconCode: weather.icon
        };
    },
    
    /**
     * 获取天气状况中文描述
     * @param {string} condition 天气状况
     * @returns {string} 中文描述
     */
    getWeatherCondition(condition) {
        const conditionMap = {
            'sunny': '晴',
            'clear': '晴',
            'cloudy': '多云',
            'overcast': '阴',
            'shower': '阵雨',
            'thunderstorm': '雷阵雨',
            'rain': '雨',
            'drizzle': '小雨',
            'snow': '雪',
            'fog': '雾',
            'haze': '霾',
            'windy': '大风'
        };
        
        // 简单的关键词匹配
        const lowerCondition = condition.toLowerCase();
        for (const [key, value] of Object.entries(conditionMap)) {
            if (lowerCondition.includes(key)) {
                return value;
            }
        }
        
        return condition; // 如果没有找到匹配，返回原始值
    },
    
    /**
     * 转换风速 (和风天气)
     * @param {string|number} windSpeed 风速
     * @param {string|number} windScale 风级
     * @returns {number} km/h单位的风速
     */
    convertWindSpeed(windSpeed, windScale) {
        // 如果有具体风速值，优先使用
        if (windSpeed && !isNaN(parseFloat(windSpeed))) {
            return Math.round(parseFloat(windSpeed));
        }
        
        // 根据风级转换为大致风速 (km/h)
        const scaleToSpeed = {
            '0': 0, '1': 2, '2': 8, '3': 15, '4': 25, '5': 35,
            '6': 47, '7': 60, '8': 75, '9': 90, '10': 105,
            '11': 120, '12': 135
        };
        
        return scaleToSpeed[windScale] || 0;
    },
    
    /**
     * 从m/s转换风速到km/h
     * @param {number} speedMps m/s单位的风速
     * @returns {number} km/h单位的风速
     */
    convertWindSpeedFromMps(speedMps) {
        if (!speedMps || isNaN(speedMps)) return 0;
        return Math.round(speedMps * 3.6); // m/s 转 km/h
    },
    
    /**
     * 获取风向描述
     * @param {string} windDir 风向文字
     * @param {number} wind360 风向角度
     * @returns {string} 风向描述
     */
    getWindDirection(windDir, wind360) {
        if (windDir) return windDir;
        
        return this.getWindDirectionFromDegrees(wind360);
    },
    
    /**
     * 根据角度获取风向
     * @param {number} degrees 风向角度
     * @returns {string} 风向描述
     */
    getWindDirectionFromDegrees(degrees) {
        if (!degrees && degrees !== 0) return '无风';
        
        const directions = [
            '北风', '东北风', '东风', '东南风',
            '南风', '西南风', '西风', '西北风'
        ];
        
        const index = Math.round(degrees / 45) % 8;
        return directions[index];
    },
    
    /**
     * 清理气压数据
     * @param {string|number} pressure 气压值
     * @returns {number} 清理后的气压值
     */
    sanitizePressure(pressure) {
        const num = parseFloat(pressure);
        if (isNaN(num) || !WeatherUtils.Validator.isInRange(num, 800, 1200)) {
            return null;
        }
        return Math.round(num);
    },
    
    /**
     * 清理能见度数据
     * @param {string|number} visibility 能见度值
     * @returns {number} 清理后的能见度值 (km)
     */
    sanitizeVisibility(visibility) {
        const num = parseFloat(visibility);
        if (isNaN(num) || num < 0) {
            return null;
        }
        return Math.round(num * 10) / 10; // 保留一位小数
    },
    
    /**
     * 获取天气图标URL
     * @param {string} iconCode 图标代码
     * @param {string} provider API提供商
     * @returns {string} 图标URL
     */
    getWeatherIconUrl(iconCode, provider = WeatherConfig.API.PROVIDER) {
        const iconMap = WeatherConfig.WEATHER_ICONS;
        let iconFile;
        
        switch (provider) {
            case 'QWEATHER':
                iconFile = iconMap.QWEATHER[iconCode] || iconMap.DEFAULT_ICON;
                break;
            case 'OPENWEATHER':
                // OpenWeatherMap 图标可以直接使用其CDN
                return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
            case 'DEMO':
            default:
                iconFile = iconMap.QWEATHER[iconCode] || iconMap.DEFAULT_ICON;
                break;
        }
        
        return iconMap.BASE_PATH + iconFile;
    },
    
    /**
     * 验证天气数据完整性
     * @param {Object} data 天气数据
     * @returns {Object} 验证结果 {isValid: boolean, errors: string[]}
     */
    validateWeatherData(data) {
        const errors = [];
        
        if (!data) {
            errors.push('天气数据为空');
            return { isValid: false, errors };
        }
        
        // 检查必要字段
        const requiredFields = {
            temperature: '温度',
            condition: '天气状况',
            humidity: '湿度'
        };
        
        Object.entries(requiredFields).forEach(([field, name]) => {
            if (data[field] === null || data[field] === undefined) {
                errors.push(`缺少${name}数据`);
            }
        });
        
        // 检查数据范围
        if (data.temperature !== null && !WeatherUtils.Validator.isInRange(data.temperature, -50, 60)) {
            errors.push('温度数据异常');
        }
        
        if (data.humidity !== null && !WeatherUtils.Validator.isInRange(data.humidity, 0, 100)) {
            errors.push('湿度数据异常');
        }
        
        WeatherUtils.Logger.debug('天气数据验证结果', { isValid: errors.length === 0, errors });
        
        return {
            isValid: errors.length === 0,
            errors
        };
    },
    
    /**
     * 获取缓存的天气数据
     * @returns {Object|null} 缓存的天气数据
     */
    getCachedWeatherData() {
        return WeatherUtils.Cache.get(WeatherConfig.CACHE.KEYS.WEATHER_DATA);
    },
    
    /**
     * 缓存天气数据
     * @param {Object} data 天气数据
     */
    cacheWeatherData(data) {
        WeatherUtils.Cache.set(
            WeatherConfig.CACHE.KEYS.WEATHER_DATA,
            data,
            WeatherConfig.CACHE.EXPIRY.WEATHER_DATA
        );
        
        // 同时保存备用缓存
        WeatherUtils.Cache.set(
            WeatherConfig.CACHE.KEYS.BACKUP_DATA,
            data,
            WeatherConfig.CACHE.EXPIRY.BACKUP_DATA
        );
        
        WeatherUtils.Cache.set(
            WeatherConfig.CACHE.KEYS.LAST_UPDATE,
            new Date().toISOString()
        );
    },
    
    /**
     * 获取备用缓存数据
     * @returns {Object|null} 备用缓存数据
     */
    getBackupData() {
        return WeatherUtils.Cache.get(WeatherConfig.CACHE.KEYS.BACKUP_DATA);
    },
    
    /**
     * 获取上次更新时间
     * @returns {string|null} 上次更新时间
     */
    getLastUpdateTime() {
        return WeatherUtils.Cache.get(WeatherConfig.CACHE.KEYS.LAST_UPDATE);
    }
};