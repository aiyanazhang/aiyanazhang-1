/**
 * 工具函数库
 * 包含通用的辅助函数和工具方法
 */

window.WeatherUtils = {
    
    /**
     * 日志工具
     */
    Logger: {
        log(level, message, data = null) {
            if (!WeatherConfig.DEBUG.ENABLED) return;
            
            const levels = ['error', 'warn', 'info', 'debug'];
            const currentLevelIndex = levels.indexOf(WeatherConfig.DEBUG.LOG_LEVEL);
            const messageLevelIndex = levels.indexOf(level);
            
            if (messageLevelIndex <= currentLevelIndex) {
                const timestamp = new Date().toISOString();
                const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
                
                if (data) {
                    console[level](prefix, message, data);
                } else {
                    console[level](prefix, message);
                }
            }
        },
        
        error(message, data) {
            this.log('error', message, data);
        },
        
        warn(message, data) {
            this.log('warn', message, data);
        },
        
        info(message, data) {
            this.log('info', message, data);
        },
        
        debug(message, data) {
            this.log('debug', message, data);
        }
    },

    /**
     * 时间工具
     */
    Time: {
        /**
         * 格式化时间
         * @param {Date|string} date 时间对象或时间字符串
         * @param {string} format 格式字符串，默认 'YYYY-MM-DD HH:mm:ss'
         * @returns {string} 格式化后的时间字符串
         */
        format(date, format = 'YYYY-MM-DD HH:mm:ss') {
            const d = new Date(date);
            if (isNaN(d.getTime())) {
                return '--';
            }
            
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            const hours = String(d.getHours()).padStart(2, '0');
            const minutes = String(d.getMinutes()).padStart(2, '0');
            const seconds = String(d.getSeconds()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },
        
        /**
         * 获取当前时间字符串
         * @param {string} format 格式字符串
         * @returns {string} 格式化的当前时间
         */
        now(format = 'YYYY-MM-DD HH:mm:ss') {
            return this.format(new Date(), format);
        },
        
        /**
         * 检查时间是否过期
         * @param {Date|string} time 时间
         * @param {number} expiry 过期时间(毫秒)
         * @returns {boolean} 是否过期
         */
        isExpired(time, expiry) {
            const now = Date.now();
            const targetTime = new Date(time).getTime();
            return (now - targetTime) > expiry;
        },
        
        /**
         * 获取相对时间描述
         * @param {Date|string} time 时间
         * @returns {string} 相对时间描述
         */
        getRelativeTime(time) {
            const now = Date.now();
            const targetTime = new Date(time).getTime();
            const diff = now - targetTime;
            
            if (diff < 60000) { // 小于1分钟
                return '刚刚';
            } else if (diff < 3600000) { // 小于1小时
                const minutes = Math.floor(diff / 60000);
                return `${minutes}分钟前`;
            } else if (diff < 86400000) { // 小于1天
                const hours = Math.floor(diff / 3600000);
                return `${hours}小时前`;
            } else {
                const days = Math.floor(diff / 86400000);
                return `${days}天前`;
            }
        }
    },

    /**
     * 缓存工具
     */
    Cache: {
        /**
         * 设置缓存
         * @param {string} key 缓存键
         * @param {any} value 缓存值
         * @param {number} expiry 过期时间(毫秒)，可选
         */
        set(key, value, expiry = null) {
            try {
                const cacheData = {
                    value: value,
                    timestamp: Date.now(),
                    expiry: expiry
                };
                
                if (WeatherConfig.CACHE.USE_MEMORY) {
                    this._memoryCache = this._memoryCache || {};
                    this._memoryCache[key] = cacheData;
                } else {
                    localStorage.setItem(key, JSON.stringify(cacheData));
                }
                
                WeatherUtils.Logger.debug(`缓存已设置: ${key}`, cacheData);
                return true;
            } catch (error) {
                WeatherUtils.Logger.error('设置缓存失败', { key, error });
                return false;
            }
        },
        
        /**
         * 获取缓存
         * @param {string} key 缓存键
         * @returns {any|null} 缓存值，如果不存在或已过期返回null
         */
        get(key) {
            try {
                let cacheData;
                
                if (WeatherConfig.CACHE.USE_MEMORY) {
                    this._memoryCache = this._memoryCache || {};
                    cacheData = this._memoryCache[key];
                } else {
                    const cached = localStorage.getItem(key);
                    if (!cached) return null;
                    cacheData = JSON.parse(cached);
                }
                
                if (!cacheData) return null;
                
                // 检查是否过期
                if (cacheData.expiry && WeatherUtils.Time.isExpired(cacheData.timestamp, cacheData.expiry)) {
                    this.remove(key);
                    WeatherUtils.Logger.debug(`缓存已过期: ${key}`);
                    return null;
                }
                
                WeatherUtils.Logger.debug(`缓存获取成功: ${key}`, cacheData);
                return cacheData.value;
            } catch (error) {
                WeatherUtils.Logger.error('获取缓存失败', { key, error });
                return null;
            }
        },
        
        /**
         * 删除缓存
         * @param {string} key 缓存键
         */
        remove(key) {
            try {
                if (WeatherConfig.CACHE.USE_MEMORY) {
                    this._memoryCache = this._memoryCache || {};
                    delete this._memoryCache[key];
                } else {
                    localStorage.removeItem(key);
                }
                WeatherUtils.Logger.debug(`缓存已删除: ${key}`);
            } catch (error) {
                WeatherUtils.Logger.error('删除缓存失败', { key, error });
            }
        },
        
        /**
         * 清空所有缓存
         */
        clear() {
            try {
                if (WeatherConfig.CACHE.USE_MEMORY) {
                    this._memoryCache = {};
                } else {
                    // 只清除天气相关的缓存
                    Object.values(WeatherConfig.CACHE.KEYS).forEach(key => {
                        localStorage.removeItem(key);
                    });
                }
                WeatherUtils.Logger.info('缓存已清空');
            } catch (error) {
                WeatherUtils.Logger.error('清空缓存失败', error);
            }
        }
    },

    /**
     * DOM操作工具
     */
    DOM: {
        /**
         * 根据ID获取元素
         * @param {string} id 元素ID
         * @returns {HTMLElement|null} DOM元素
         */
        getElementById(id) {
            return document.getElementById(id);
        },
        
        /**
         * 设置元素文本内容
         * @param {string|HTMLElement} element 元素ID或元素对象
         * @param {string} text 文本内容
         */
        setText(element, text) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.textContent = text;
            }
        },
        
        /**
         * 设置元素HTML内容
         * @param {string|HTMLElement} element 元素ID或元素对象
         * @param {string} html HTML内容
         */
        setHTML(element, html) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.innerHTML = html;
            }
        },
        
        /**
         * 显示元素
         * @param {string|HTMLElement} element 元素ID或元素对象
         */
        show(element) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.style.display = '';
                el.classList.remove('hidden');
            }
        },
        
        /**
         * 隐藏元素
         * @param {string|HTMLElement} element 元素ID或元素对象
         */
        hide(element) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.style.display = 'none';
                el.classList.add('hidden');
            }
        },
        
        /**
         * 切换元素显示状态
         * @param {string|HTMLElement} element 元素ID或元素对象
         * @param {boolean} show 是否显示
         */
        toggle(element, show) {
            if (show) {
                this.show(element);
            } else {
                this.hide(element);
            }
        },
        
        /**
         * 添加CSS类
         * @param {string|HTMLElement} element 元素ID或元素对象
         * @param {string} className CSS类名
         */
        addClass(element, className) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.classList.add(className);
            }
        },
        
        /**
         * 移除CSS类
         * @param {string|HTMLElement} element 元素ID或元素对象
         * @param {string} className CSS类名
         */
        removeClass(element, className) {
            const el = typeof element === 'string' ? this.getElementById(element) : element;
            if (el) {
                el.classList.remove(className);
            }
        }
    },

    /**
     * 网络工具
     */
    Network: {
        /**
         * 检查网络连接状态
         * @returns {boolean} 是否在线
         */
        isOnline() {
            return navigator.onLine;
        },
        
        /**
         * HTTP请求封装
         * @param {string} url 请求URL
         * @param {Object} options 请求选项
         * @returns {Promise} 请求Promise
         */
        async request(url, options = {}) {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: WeatherConfig.API.TIMEOUT
            };
            
            const finalOptions = { ...defaultOptions, ...options };
            
            // 创建AbortController用于超时控制
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);
            
            try {
                const response = await fetch(url, {
                    ...finalOptions,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                WeatherUtils.Logger.debug('网络请求成功', { url, data });
                return data;
                
            } catch (error) {
                clearTimeout(timeoutId);
                
                if (error.name === 'AbortError') {
                    throw new Error('请求超时');
                }
                
                WeatherUtils.Logger.error('网络请求失败', { url, error });
                throw error;
            }
        },
        
        /**
         * 重试机制
         * @param {Function} fn 要重试的函数
         * @param {number} times 重试次数
         * @param {number} delay 重试延迟
         * @returns {Promise} 重试结果
         */
        async retry(fn, times = WeatherConfig.API.RETRY_TIMES, delay = WeatherConfig.API.RETRY_DELAY) {
            let lastError;
            
            for (let i = 0; i <= times; i++) {
                try {
                    return await fn();
                } catch (error) {
                    lastError = error;
                    WeatherUtils.Logger.warn(`重试 ${i + 1}/${times + 1} 失败`, error);
                    
                    if (i < times) {
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                }
            }
            
            throw lastError;
        }
    },

    /**
     * 数据验证工具
     */
    Validator: {
        /**
         * 验证天气数据结构
         * @param {Object} data 天气数据
         * @returns {boolean} 是否有效
         */
        isValidWeatherData(data) {
            if (!data || typeof data !== 'object') {
                return false;
            }
            
            const requiredFields = ['temperature', 'condition', 'humidity'];
            return requiredFields.every(field => data.hasOwnProperty(field) && data[field] !== null && data[field] !== undefined);
        },
        
        /**
         * 验证数字范围
         * @param {number} value 数值
         * @param {number} min 最小值
         * @param {number} max 最大值
         * @returns {boolean} 是否在范围内
         */
        isInRange(value, min, max) {
            return typeof value === 'number' && value >= min && value <= max;
        },
        
        /**
         * 清理和验证温度值
         * @param {any} temp 温度值
         * @returns {number|null} 清理后的温度值
         */
        sanitizeTemperature(temp) {
            const num = parseFloat(temp);
            if (isNaN(num) || !this.isInRange(num, -100, 100)) {
                return null;
            }
            return Math.round(num * 10) / 10; // 保留一位小数
        },
        
        /**
         * 清理和验证湿度值
         * @param {any} humidity 湿度值
         * @returns {number|null} 清理后的湿度值
         */
        sanitizeHumidity(humidity) {
            const num = parseInt(humidity);
            if (isNaN(num) || !this.isInRange(num, 0, 100)) {
                return null;
            }
            return num;
        }
    },

    /**
     * 通用工具函数
     */
    Common: {
        /**
         * 防抖函数
         * @param {Function} func 要防抖的函数
         * @param {number} wait 等待时间
         * @returns {Function} 防抖后的函数
         */
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        /**
         * 节流函数
         * @param {Function} func 要节流的函数
         * @param {number} limit 限制时间
         * @returns {Function} 节流后的函数
         */
        throttle(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        /**
         * 深拷贝对象
         * @param {any} obj 要拷贝的对象
         * @returns {any} 拷贝后的对象
         */
        deepClone(obj) {
            if (obj === null || typeof obj !== 'object') {
                return obj;
            }
            
            if (obj instanceof Date) {
                return new Date(obj.getTime());
            }
            
            if (obj instanceof Array) {
                return obj.map(item => this.deepClone(item));
            }
            
            if (typeof obj === 'object') {
                const cloned = {};
                Object.keys(obj).forEach(key => {
                    cloned[key] = this.deepClone(obj[key]);
                });
                return cloned;
            }
        },
        
        /**
         * 生成唯一ID
         * @returns {string} 唯一ID
         */
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        }
    }
};
