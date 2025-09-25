# 北京朝阳区天气显示页面

一个基于HTML、CSS和JavaScript的单页面天气显示应用，专门用于显示北京朝阳区的实时天气信息。

## 项目特色

### 🌤️ 核心功能
- **实时天气数据**：显示北京朝阳区当前天气状况
- **详细气象信息**：温度、湿度、风速、气压、能见度等完整数据
- **智能缓存机制**：离线也能显示历史数据
- **自动刷新**：定时获取最新天气信息
- **错误处理**：网络异常时的优雅降级

### 🎨 用户体验
- **响应式设计**：完美适配手机、平板、桌面设备
- **现代化界面**：简洁美观的Material Design风格
- **流畅动画**：平滑的加载和切换效果
- **深色模式**：自动适配系统主题偏好
- **无障碍支持**：遵循WCAG可访问性标准

### ⚡ 技术亮点
- **纯原生JavaScript**：无框架依赖，轻量高效
- **模块化架构**：清晰的代码组织和职责分离
- **缓存策略**：多层次缓存确保可用性
- **API兼容**：支持多个天气数据提供商
- **性能优化**：懒加载、防抖、节流等性能技术

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd beijing-weather
```

### 2. 配置API密钥
编辑 `src/js/config.js` 文件，设置你的天气API密钥：

```javascript
// 和风天气API (推荐)
QWEATHER: {
    KEY: 'YOUR_QWEATHER_API_KEY', // 替换为你的API密钥
    // ... 其他配置
}

// 或者使用OpenWeatherMap
OPENWEATHER: {
    KEY: 'YOUR_OPENWEATHER_API_KEY', // 替换为你的API密钥
    // ... 其他配置
}
```

### 3. 启动应用

#### 方法一：本地服务器
```bash
# 使用Python内置服务器
python -m http.server 8000

# 或使用Node.js的http-server
npx http-server -p 8000
```

#### 方法二：直接打开
由于使用了现代Web API，建议使用本地服务器而不是直接打开HTML文件。

### 4. 访问应用
打开浏览器访问：`http://localhost:8000`

## 项目结构

```
beijing-weather/
├── index.html                 # 主页面
├── src/                      # 源代码目录
│   ├── css/                  # 样式文件
│   │   ├── styles.css        # 主要样式
│   │   └── responsive.css    # 响应式样式
│   ├── js/                   # JavaScript文件
│   │   ├── config.js         # 配置文件
│   │   ├── utils.js          # 工具函数
│   │   ├── weather-api.js    # API服务
│   │   ├── ui-controller.js  # UI控制器
│   │   └── app.js           # 主应用
│   └── images/              # 图片资源
│       └── weather-icons/   # 天气图标
├── docs/                    # 文档目录
├── tests/                   # 测试文件
└── README.md               # 项目说明
```

## 配置说明

### API提供商选择

项目支持多个天气API提供商：

#### 和风天气 (推荐用于中国地区)
- 注册地址：https://dev.qweather.com/
- 优势：中文支持好，国内访问速度快
- 免费额度：1000次/天

#### OpenWeatherMap (国际通用)
- 注册地址：https://openweathermap.org/api
- 优势：数据准确，全球覆盖
- 免费额度：1000次/天

#### 演示模式
```javascript
// 在config.js中设置
API: {
    PROVIDER: 'DEMO', // 使用演示数据，无需API密钥
}
```

### 缓存配置

```javascript
// 缓存有效期设置
CACHE: {
    EXPIRY: {
        WEATHER_DATA: 30 * 60 * 1000, // 30分钟
        BACKUP_DATA: 24 * 60 * 60 * 1000 // 24小时
    }
}
```

### 自动刷新设置

```javascript
// UI配置
UI: {
    AUTO_REFRESH_INTERVAL: 10 * 60 * 1000, // 10分钟自动刷新
}
```

## 功能详解

### 🌡️ 天气数据显示
- **当前温度**：实时温度和体感温度
- **天气状况**：文字描述和图标显示
- **详细信息**：湿度、风速风向、气压、能见度

### 💾 缓存策略
- **主缓存**：30分钟有效期的最新数据
- **备用缓存**：24小时有效期的备用数据
- **离线支持**：网络异常时使用缓存数据

### 🔄 自动刷新
- **定时刷新**：每10分钟自动获取新数据
- **智能暂停**：页面不可见时暂停刷新
- **网络感知**：网络恢复时自动刷新

### 📱 响应式设计

#### 断点设置
- **手机**：< 576px - 单列布局
- **平板**：576px - 768px - 两列布局
- **桌面**：> 768px - 多列网格布局

#### 适配特性
- **触摸优化**：按钮大小适合触摸操作
- **字体缩放**：根据屏幕大小调整字体
- **布局重排**：组件自动重新排列

## 开发指南

### 代码架构

项目采用模块化架构，主要模块包括：

#### WeatherConfig
全局配置管理，包含API设置、UI配置、错误消息等。

#### WeatherUtils
工具函数库，提供日志、缓存、DOM操作、网络请求等通用功能。

#### WeatherAPI
天气API服务，负责数据获取、转换和验证。

#### UIController
UI控制器，管理页面元素显示和用户交互。

#### WeatherApp
主应用程序，协调各模块工作。

### 扩展开发

#### 添加新的天气API
1. 在 `weather-api.js` 中添加新的API方法
2. 更新 `config.js` 中的API配置
3. 实现数据转换函数

#### 自定义主题
1. 修改 `styles.css` 中的CSS变量
2. 添加新的主题切换逻辑
3. 更新响应式设计

#### 添加新功能
1. 在相应模块中添加功能代码
2. 更新UI控制器支持新功能
3. 添加配置选项

### 调试工具

开发模式下可以使用调试工具：

```javascript
// 在浏览器控制台中使用
DebugWeatherApp.getStatus();     // 获取应用状态
DebugWeatherApp.clearCache();    // 清除缓存
DebugWeatherApp.reload();        // 重新加载应用
```

## 部署指南

### 静态部署
项目是纯静态页面，可以部署到任何静态托管服务：

- **GitHub Pages**
- **Netlify**
- **Vercel**
- **阿里云OSS**
- **腾讯云COS**

### 配置优化
1. **压缩资源**：压缩CSS和JavaScript文件
2. **图片优化**：优化天气图标大小
3. **缓存设置**：设置合适的浏览器缓存策略
4. **HTTPS部署**：确保安全连接

### 生产环境配置
```javascript
// 生产环境关闭调试
DEBUG: {
    ENABLED: false,
    LOG_LEVEL: 'error'
}
```

## 浏览器兼容性

### 支持的浏览器
- **Chrome** 60+
- **Firefox** 55+
- **Safari** 12+
- **Edge** 79+

### 使用的现代API
- Fetch API
- Promises/async-await
- CSS Grid和Flexbox
- CSS Custom Properties
- Local Storage

### 兼容性处理
项目使用了Polyfill和降级策略来支持较老的浏览器。

## 性能优化

### 加载优化
- **资源压缩**：CSS和JS文件压缩
- **图片优化**：WebP格式和懒加载
- **缓存策略**：合理的缓存头设置

### 运行时优化
- **防抖节流**：用户交互优化
- **内存管理**：避免内存泄漏
- **DOM操作**：批量操作和虚拟滚动

### 网络优化
- **请求合并**：减少HTTP请求
- **错误重试**：智能重试机制
- **离线支持**：Service Worker缓存

## 测试

### 功能测试
- 天气数据获取和显示
- 缓存机制测试
- 错误处理测试
- 响应式布局测试

### 性能测试
- 页面加载速度
- 内存使用情况
- API响应时间
- 缓存命中率

### 兼容性测试
- 不同浏览器测试
- 不同设备测试
- 网络环境测试

## 贡献指南

### 贡献方式
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

### 代码规范
- 使用ESLint代码检查
- 遵循JavaScript Standard Style
- 添加适当的注释
- 保持代码简洁清晰

### 提交规范
```
type(scope): description

[optional body]

[optional footer]
```

## 许可证

本项目采用 MIT 许可证，详情请查看 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- **Issue**：在GitHub上提交Issue
- **Email**：project@example.com
- **文档**：查看项目Wiki

## 更新日志

### v1.0.0 (2024-01-15)
- 🎉 初始版本发布
- ✨ 基础天气显示功能
- 📱 响应式设计支持
- 💾 缓存机制实现
- 🔄 自动刷新功能

---

**感谢使用北京朝阳区天气显示页面！** 🌤️