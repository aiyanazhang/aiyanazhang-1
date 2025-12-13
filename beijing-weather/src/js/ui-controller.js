/**
 * UI控制器
 * 负责页面元素的显示和交互控制
 */

window.UIController = {
    
    // DOM元素引用
    elements: {
        // 容器元素
        loadingContainer: null,
        errorContainer: null,
        weatherDisplay: null,
        
        // 头部元素
        currentTime: null,
        refreshBtn: null,
        
        // 天气信息元素
        locationName: null,
        updateTime: null,
        weatherIcon: null,
        currentTemp: null,
        feelsLike: null,
        conditionText: null,
        conditionDesc: null,
        
        // 详细信息元素
        humidity: null,
        windSpeed: null,
        windDirection: null,
        pressure: null,
        visibility: null,
        
        // 错误处理元素
        errorMessage: null,
        retryBtn: null,
        dataSource: null
    },
    
    /**
     * 初始化UI控制器
     */
    init() {
        WeatherUtils.Logger.info('初始化UI控制器');
        this.initElements();
        this.bindEvents();
        this.startClock();
        this.showLoading();
    },
    
    /**
     * 初始化DOM元素引用
     */
    initElements() {
        const elementIds = {
            // 容器
            loadingContainer: 'loadingContainer',
            errorContainer: 'errorContainer',
            weatherDisplay: 'weatherDisplay',
            
            // 头部
            currentTime: 'currentTime',
            refreshBtn: 'refreshBtn',
            
            // 天气信息
            locationName: 'locationName',
            updateTime: 'updateTime',
            weatherIcon: 'weatherIcon',
            currentTemp: 'currentTemp',
            feelsLike: 'feelsLike',
            conditionText: 'conditionText',
            conditionDesc: 'conditionDesc',
            
            // 详细信息
            humidity: 'humidity',
            windSpeed: 'windSpeed',
            windDirection: 'windDirection',
            pressure: 'pressure',
            visibility: 'visibility',
            
            // 错误处理
            errorMessage: 'errorMessage',
            retryBtn: 'retryBtn',
            dataSource: 'dataSource'
        };
        
        // 获取所有元素引用
        Object.entries(elementIds).forEach(([key, id]) => {
            this.elements[key] = WeatherUtils.DOM.getElementById(id);
            if (!this.elements[key]) {
                WeatherUtils.Logger.warn(`找不到元素: ${id}`);
            }
        });
    },
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 刷新按钮点击事件
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => {
                this.onRefreshClick();
            });
        }
        
        // 重试按钮点击事件
        if (this.elements.retryBtn) {
            this.elements.retryBtn.addEventListener('click', () => {
                this.onRetryClick();
            });
        }
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
                this.onRefreshClick();
            }
        });
        
        // 网络状态变化事件
        window.addEventListener('online', () => {
            this.showNetworkStatus(true);
            // 网络恢复时自动刷新
            setTimeout(() => this.onRefreshClick(), 1000);
        });
        
        window.addEventListener('offline', () => {
            this.showNetworkStatus(false);
        });
        
        // 页面可见性变化事件
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.updateClock();
                // 页面重新可见时检查数据是否需要更新
                this.checkDataFreshness();
            }
        });
    },
    
    /**
     * 刷新按钮点击处理
     */
    onRefreshClick() {
        WeatherUtils.Logger.info('用户点击刷新按钮');
        
        if (this.elements.refreshBtn) {
            WeatherUtils.DOM.addClass(this.elements.refreshBtn, 'loading');
            this.elements.refreshBtn.disabled = true;
        }
        
        // 触发数据刷新事件
        this.dispatchEvent('refresh-requested');
    },
    
    /**
     * 重试按钮点击处理
     */
    onRetryClick() {
        WeatherUtils.Logger.info('用户点击重试按钮');
        this.showLoading();
        this.dispatchEvent('retry-requested');
    },
    
    /**
     * 显示加载状态
     */
    showLoading() {
        WeatherUtils.Logger.debug('显示加载状态');
        
        WeatherUtils.DOM.show(this.elements.loadingContainer);
        WeatherUtils.DOM.hide(this.elements.errorContainer);
        WeatherUtils.DOM.hide(this.elements.weatherDisplay);
        
        // 禁用刷新按钮
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.disabled = true;
            WeatherUtils.DOM.addClass(this.elements.refreshBtn, 'loading');
        }
    },
    
    /**
     * 显示错误状态
     * @param {string} message 错误消息
     * @param {boolean} showRetry 是否显示重试按钮
     */
    showError(message, showRetry = true) {
        WeatherUtils.Logger.debug('显示错误状态', { message, showRetry });
        
        WeatherUtils.DOM.hide(this.elements.loadingContainer);
        WeatherUtils.DOM.show(this.elements.errorContainer);
        WeatherUtils.DOM.hide(this.elements.weatherDisplay);
        
        // 设置错误消息
        if (this.elements.errorMessage) {
            WeatherUtils.DOM.setText(this.elements.errorMessage, message);
        }
        
        // 控制重试按钮显示
        if (this.elements.retryBtn) {
            WeatherUtils.DOM.toggle(this.elements.retryBtn, showRetry);
        }
        
        // 重置刷新按钮状态
        this.resetRefreshButton();
    },
    
    /**
     * 显示天气数据
     * @param {Object} data 天气数据
     */
    showWeatherData(data) {
        WeatherUtils.Logger.debug('显示天气数据', data);
        
        try {
            // 隐藏加载和错误状态
            WeatherUtils.DOM.hide(this.elements.loadingContainer);
            WeatherUtils.DOM.hide(this.elements.errorContainer);
            
            // 更新天气信息
            this.updateWeatherInfo(data);
            
            // 显示天气展示区域
            WeatherUtils.DOM.show(this.elements.weatherDisplay);
            
            // 重置刷新按钮状态
            this.resetRefreshButton();
            
            // 添加数据加载动画
            if (this.elements.weatherDisplay) {
                WeatherUtils.DOM.removeClass(this.elements.weatherDisplay, 'fadeIn');
                // 强制重排后重新添加动画类
                this.elements.weatherDisplay.offsetHeight;
                WeatherUtils.DOM.addClass(this.elements.weatherDisplay, 'fadeIn');
            }
            
        } catch (error) {
            WeatherUtils.Logger.error('显示天气数据时出错', error);
            this.showError('显示天气数据时出现错误');
        }
    },
    
    /**
     * 更新天气信息
     * @param {Object} data 天气数据
     */
    updateWeatherInfo(data) {
        // 位置信息
        if (this.elements.locationName && data.location) {
            WeatherUtils.DOM.setText(this.elements.locationName, data.location);
        }
        
        // 更新时间
        if (this.elements.updateTime && data.updateTime) {
            const updateTimeStr = WeatherUtils.Time.format(data.updateTime);
            WeatherUtils.DOM.setText(this.elements.updateTime, updateTimeStr);
        }
        
        // 天气图标
        if (this.elements.weatherIcon && data.iconCode) {
            const iconUrl = WeatherAPI.getWeatherIconUrl(data.iconCode);
            this.elements.weatherIcon.src = iconUrl;
            this.elements.weatherIcon.alt = data.condition || '天气图标';
        }
        
        // 当前温度
        if (this.elements.currentTemp && data.temperature !== null) {
            WeatherUtils.DOM.setText(this.elements.currentTemp, Math.round(data.temperature));
        }
        
        // 体感温度
        if (this.elements.feelsLike && data.feelsLike !== null) {
            WeatherUtils.DOM.setText(this.elements.feelsLike, Math.round(data.feelsLike));
        }
        
        // 天气状况
        if (this.elements.conditionText && data.condition) {
            WeatherUtils.DOM.setText(this.elements.conditionText, data.condition);
        }
        
        if (this.elements.conditionDesc && data.condition) {
            WeatherUtils.DOM.setText(this.elements.conditionDesc, `今日${data.condition}`);
        }
        
        // 详细信息
        this.updateDetailInfo('humidity', data.humidity, '%');
        this.updateDetailInfo('windSpeed', data.windSpeed, 'km/h');
        this.updateDetailInfo('pressure', data.pressure, 'hPa');
        this.updateDetailInfo('visibility', data.visibility, 'km');
        
        // 风向信息
        if (this.elements.windDirection && data.windDirection) {
            WeatherUtils.DOM.setText(this.elements.windDirection, data.windDirection);
        }
        
        // 数据源信息
        if (this.elements.dataSource) {
            const sourceText = this.getDataSourceText();
            WeatherUtils.DOM.setText(this.elements.dataSource, sourceText);
        }
    },
    
    /**
     * 更新详细信息项
     * @param {string} elementKey 元素键名
     * @param {any} value 数值
     * @param {string} unit 单位
     */
    updateDetailInfo(elementKey, value, unit) {
        const element = this.elements[elementKey];
        if (element && value !== null && value !== undefined) {
            const displayValue = typeof value === 'number' ? Math.round(value * 10) / 10 : value;
            WeatherUtils.DOM.setText(element, `${displayValue} ${unit}`);
        } else if (element) {
            WeatherUtils.DOM.setText(element, `-- ${unit}`);
        }
    },
    
    /**
     * 获取数据源文本
     * @returns {string} 数据源描述
     */
    getDataSourceText() {
        switch (WeatherConfig.API.PROVIDER) {
            case 'QWEATHER':
                return '和风天气';
            case 'OPENWEATHER':
                return 'OpenWeatherMap';
            case 'DEMO':
                return '演示数据';
            default:
                return '天气API';
        }
    },
    
    /**
     * 重置刷新按钮状态
     */
    resetRefreshButton() {
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.disabled = false;
            WeatherUtils.DOM.removeClass(this.elements.refreshBtn, 'loading');
        }
    },
    
    /**
     * 开始时钟
     */
    startClock() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    },
    
    /**
     * 更新时钟显示
     */
    updateClock() {
        if (this.elements.currentTime) {
            const now = WeatherUtils.Time.now('MM-DD HH:mm:ss');
            WeatherUtils.DOM.setText(this.elements.currentTime, now);
        }
    },
    
    /**
     * 显示网络状态
     * @param {boolean} isOnline 是否在线
     */
    showNetworkStatus(isOnline) {
        const statusClass = isOnline ? 'online' : 'offline';
        const statusText = isOnline ? '网络已连接' : '网络已断开';
        
        // 可以在这里添加网络状态指示器的逻辑
        WeatherUtils.Logger.info(`网络状态: ${statusText}`);
        
        // 显示临时提示
        this.showTemporaryMessage(statusText, statusClass);
    },
    
    /**
     * 显示临时消息
     * @param {string} message 消息内容
     * @param {string} type 消息类型
     * @param {number} duration 显示时长 (毫秒)
     */
    showTemporaryMessage(message, type = 'info', duration = 3000) {
        // 创建临时消息元素
        const messageEl = document.createElement('div');
        messageEl.className = `temp-message ${type}`;
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'online' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 8px;
            z-index: 1000;
            opacity: 0;
            transform: translateX(100px);
            transition: all 0.3s ease-in-out;
        `;
        
        document.body.appendChild(messageEl);
        
        // 显示动画
        setTimeout(() => {
            messageEl.style.opacity = '1';
            messageEl.style.transform = 'translateX(0)';
        }, 100);
        
        // 隐藏和移除
        setTimeout(() => {
            messageEl.style.opacity = '0';
            messageEl.style.transform = 'translateX(100px)';
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.parentNode.removeChild(messageEl);
                }
            }, 300);
        }, duration);
    },
    
    /**
     * 检查数据新鲜度
     */
    checkDataFreshness() {
        const lastUpdate = WeatherAPI.getLastUpdateTime();
        if (lastUpdate) {
            const updateTime = new Date(lastUpdate);
            const now = new Date();
            const diff = now - updateTime;
            
            // 如果数据超过1小时，提示用户刷新
            if (diff > 60 * 60 * 1000) {
                WeatherUtils.Logger.info('数据较旧，建议刷新');
                this.showTemporaryMessage('数据可能已过时，建议刷新', 'warning', 5000);
            }
        }
    },
    
    /**
     * 分发自定义事件
     * @param {string} eventName 事件名称
     * @param {any} detail 事件详情
     */
    dispatchEvent(eventName, detail = null) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    },
    
    /**
     * 显示缓存数据提示
     * @param {string} cacheTime 缓存时间
     */
    showCachedDataWarning(cacheTime) {
        const relativeTime = WeatherUtils.Time.getRelativeTime(cacheTime);
        this.showTemporaryMessage(`显示缓存数据 (${relativeTime})`, 'warning', 5000);
    },
    
    /**
     * 获取当前显示状态
     * @returns {string} 显示状态: 'loading', 'error', 'weather', 'hidden'
     */
    getCurrentState() {
        if (this.elements.loadingContainer && !this.elements.loadingContainer.style.display === 'none') {
            return 'loading';
        }
        if (this.elements.errorContainer && !this.elements.errorContainer.style.display === 'none') {
            return 'error';
        }
        if (this.elements.weatherDisplay && !this.elements.weatherDisplay.style.display === 'none') {
            return 'weather';
        }
        return 'hidden';
    }
};