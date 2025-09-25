/**
 * 主应用程序
 * 应用入口和整体协调控制
 */

window.WeatherApp = {
    
    // 应用状态
    state: {
        isInitialized: false,
        isLoading: false,
        hasError: false,
        lastDataTime: null,
        autoRefreshTimer: null
    },
    
    /**
     * 应用初始化
     */
    async init() {
        WeatherUtils.Logger.info('开始初始化天气应用');
        
        try {
            // 等待DOM加载完成
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // 初始化UI控制器
            UIController.init();
            
            // 绑定应用级事件
            this.bindEvents();
            
            // 加载天气数据
            await this.loadWeatherData();
            
            // 启动自动刷新
            this.startAutoRefresh();
            
            // 标记应用已初始化
            this.state.isInitialized = true;
            
            WeatherUtils.Logger.info('天气应用初始化完成');
            
        } catch (error) {
            WeatherUtils.Logger.error('应用初始化失败', error);
            this.handleError(error, '应用初始化失败');
        }
    },
    
    /**
     * 绑定应用级事件
     */
    bindEvents() {
        // 监听UI控制器的事件
        document.addEventListener('refresh-requested', () => {
            this.refreshWeatherData();
        });
        
        document.addEventListener('retry-requested', () => {
            this.loadWeatherData();
        });
        
        // 监听页面卸载事件
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // 监听错误事件
        window.addEventListener('error', (event) => {
            WeatherUtils.Logger.error('全局错误', event.error);
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            WeatherUtils.Logger.error('未处理的Promise拒绝', event.reason);
        });
    },
    
    /**
     * 加载天气数据
     */
    async loadWeatherData() {
        if (this.state.isLoading) {
            WeatherUtils.Logger.debug('数据加载中，跳过重复请求');
            return;
        }
        
        this.state.isLoading = true;
        this.state.hasError = false;
        
        WeatherUtils.Logger.info('开始加载天气数据');
        
        try {
            // 首先尝试从缓存获取数据
            const cachedData = WeatherAPI.getCachedWeatherData();
            if (cachedData && this.isValidCachedData(cachedData)) {
                WeatherUtils.Logger.info('使用缓存数据');
                UIController.showWeatherData(cachedData);
                UIController.showCachedDataWarning(cachedData.updateTime);
                this.state.lastDataTime = cachedData.updateTime;
            }
            
            // 获取新的天气数据
            const weatherData = await WeatherAPI.getWeatherData();
            
            // 验证数据
            const validation = WeatherAPI.validateWeatherData(weatherData);
            if (!validation.isValid) {
                throw new Error('天气数据验证失败: ' + validation.errors.join(', '));
            }
            
            // 缓存数据
            WeatherAPI.cacheWeatherData(weatherData);
            
            // 显示数据
            UIController.showWeatherData(weatherData);
            this.state.lastDataTime = weatherData.updateTime;
            
            WeatherUtils.Logger.info('天气数据加载成功', weatherData);
            
        } catch (error) {
            WeatherUtils.Logger.error('加载天气数据失败', error);
            await this.handleDataLoadError(error);
        } finally {
            this.state.isLoading = false;
        }
    },
    
    /**
     * 刷新天气数据 (强制从API获取)
     */
    async refreshWeatherData() {
        WeatherUtils.Logger.info('强制刷新天气数据');
        
        // 清除相关缓存
        WeatherUtils.Cache.remove(WeatherConfig.CACHE.KEYS.WEATHER_DATA);
        
        // 重新加载数据
        await this.loadWeatherData();
    },
    
    /**
     * 处理数据加载错误
     * @param {Error} error 错误对象
     */
    async handleDataLoadError(error) {
        this.state.hasError = true;
        
        // 尝试使用备用缓存数据
        const backupData = WeatherAPI.getBackupData();
        if (backupData && this.isValidCachedData(backupData)) {
            WeatherUtils.Logger.info('使用备用缓存数据');
            UIController.showWeatherData(backupData);
            UIController.showCachedDataWarning(backupData.updateTime);
            
            // 显示错误提示但不阻断显示
            UIController.showTemporaryMessage(
                '获取最新数据失败，显示缓存数据',
                'warning',
                5000
            );
            return;
        }
        
        // 根据错误类型显示相应的错误信息
        let errorMessage = WeatherConfig.ERROR_MESSAGES.UNKNOWN_ERROR;
        
        if (error.message.includes('网络') || error.message.includes('timeout') || error.message.includes('超时')) {
            errorMessage = WeatherConfig.ERROR_MESSAGES.NETWORK_ERROR;
        } else if (error.message.includes('API') || error.message.includes('请求')) {
            errorMessage = WeatherConfig.ERROR_MESSAGES.API_ERROR;
        } else if (error.message.includes('数据') || error.message.includes('验证')) {
            errorMessage = WeatherConfig.ERROR_MESSAGES.INVALID_DATA;
        }
        
        UIController.showError(errorMessage, true);
    },
    
    /**
     * 通用错误处理
     * @param {Error} error 错误对象
     * @param {string} context 错误上下文
     */
    handleError(error, context = '操作') {
        WeatherUtils.Logger.error(`${context}出错`, error);
        
        this.state.hasError = true;
        
        const errorMessage = `${context}: ${error.message || '未知错误'}`;
        UIController.showError(errorMessage, true);
    },
    
    /**
     * 验证缓存数据是否有效
     * @param {Object} data 缓存数据
     * @returns {boolean} 是否有效
     */
    isValidCachedData(data) {
        if (!data) return false;
        
        // 检查基本字段
        const validation = WeatherAPI.validateWeatherData(data);
        if (!validation.isValid) {
            WeatherUtils.Logger.debug('缓存数据验证失败', validation.errors);
            return false;
        }
        
        // 检查数据是否过旧 (超过24小时的数据认为无效)
        if (data.updateTime) {
            const maxAge = 24 * 60 * 60 * 1000; // 24小时
            if (WeatherUtils.Time.isExpired(data.updateTime, maxAge)) {
                WeatherUtils.Logger.debug('缓存数据过旧');
                return false;
            }
        }
        
        return true;
    },
    
    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
        // 清除之前的定时器
        if (this.state.autoRefreshTimer) {
            clearInterval(this.state.autoRefreshTimer);
        }
        
        const interval = WeatherConfig.UI.AUTO_REFRESH_INTERVAL;
        
        this.state.autoRefreshTimer = setInterval(async () => {
            WeatherUtils.Logger.info('自动刷新天气数据');
            
            // 检查页面是否可见
            if (document.hidden) {
                WeatherUtils.Logger.debug('页面不可见，跳过自动刷新');
                return;
            }
            
            // 检查网络状态
            if (!WeatherUtils.Network.isOnline()) {
                WeatherUtils.Logger.debug('网络不可用，跳过自动刷新');
                return;
            }
            
            // 静默刷新 (不显示加载状态)
            try {
                const weatherData = await WeatherAPI.getWeatherData();
                const validation = WeatherAPI.validateWeatherData(weatherData);
                
                if (validation.isValid) {
                    WeatherAPI.cacheWeatherData(weatherData);
                    UIController.showWeatherData(weatherData);
                    this.state.lastDataTime = weatherData.updateTime;
                    
                    WeatherUtils.Logger.info('自动刷新成功');
                } else {
                    WeatherUtils.Logger.warn('自动刷新获取的数据无效', validation.errors);
                }
                
            } catch (error) {
                WeatherUtils.Logger.warn('自动刷新失败', error);
                // 自动刷新失败不显示错误界面，保持当前显示
            }
            
        }, interval);
        
        WeatherUtils.Logger.info(`自动刷新已启动，间隔: ${interval / 1000 / 60}分钟`);
    },
    
    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.state.autoRefreshTimer) {
            clearInterval(this.state.autoRefreshTimer);
            this.state.autoRefreshTimer = null;
            WeatherUtils.Logger.info('自动刷新已停止');
        }
    },
    
    /**
     * 获取应用状态
     * @returns {Object} 应用状态信息
     */
    getAppStatus() {
        return {
            isInitialized: this.state.isInitialized,
            isLoading: this.state.isLoading,
            hasError: this.state.hasError,
            lastDataTime: this.state.lastDataTime,
            autoRefreshEnabled: !!this.state.autoRefreshTimer,
            uiState: UIController.getCurrentState(),
            cacheStatus: this.getCacheStatus(),
            networkStatus: WeatherUtils.Network.isOnline()
        };
    },
    
    /**
     * 获取缓存状态
     * @returns {Object} 缓存状态信息
     */
    getCacheStatus() {
        const mainCache = WeatherAPI.getCachedWeatherData();
        const backupCache = WeatherAPI.getBackupData();
        const lastUpdate = WeatherAPI.getLastUpdateTime();
        
        return {
            hasMainCache: !!mainCache,
            hasBackupCache: !!backupCache,
            lastUpdate: lastUpdate,
            cacheAge: lastUpdate ? Date.now() - new Date(lastUpdate).getTime() : null
        };
    },
    
    /**
     * 清理资源
     */
    cleanup() {
        WeatherUtils.Logger.info('清理应用资源');
        
        // 停止自动刷新
        this.stopAutoRefresh();
        
        // 清理可能的内存泄漏
        this.state = {
            isInitialized: false,
            isLoading: false,
            hasError: false,
            lastDataTime: null,
            autoRefreshTimer: null
        };
    },
    
    /**
     * 重置应用状态
     */
    reset() {
        WeatherUtils.Logger.info('重置应用状态');
        
        // 停止自动刷新
        this.stopAutoRefresh();
        
        // 清除缓存
        WeatherUtils.Cache.clear();
        
        // 重置状态
        this.state = {
            isInitialized: false,
            isLoading: false,
            hasError: false,
            lastDataTime: null,
            autoRefreshTimer: null
        };
        
        // 重新初始化
        this.init();
    }
};

// 全局错误处理
window.addEventListener('error', (event) => {
    WeatherUtils.Logger.error('全局JavaScript错误', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
});

window.addEventListener('unhandledrejection', (event) => {
    WeatherUtils.Logger.error('未捕获的Promise拒绝', event.reason);
});

// 应用启动
document.addEventListener('DOMContentLoaded', () => {
    WeatherUtils.Logger.info('DOM加载完成，启动天气应用');
    WeatherApp.init().catch(error => {
        WeatherUtils.Logger.error('应用启动失败', error);
        console.error('Weather App failed to start:', error);
    });
});

// 导出到全局作用域以便调试
if (WeatherConfig.DEBUG.ENABLED) {
    window.DebugWeatherApp = {
        app: WeatherApp,
        ui: UIController,
        api: WeatherAPI,
        utils: WeatherUtils,
        config: WeatherConfig,
        
        // 调试方法
        getStatus: () => WeatherApp.getAppStatus(),
        clearCache: () => WeatherUtils.Cache.clear(),
        testError: () => { throw new Error('测试错误'); },
        reload: () => WeatherApp.reset()
    };
    
    console.log('调试工具已加载，使用 DebugWeatherApp 进行调试');
}