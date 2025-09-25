# 天气应用 (Weather App)

一个现代化的React天气应用程序，专注于清晰直观地显示温度和湿度信息。

## 🚀 项目特性

- **简洁明了的界面**: 突出显示温度和湿度两个核心信息
- **响应式设计**: 完美适配桌面端、平板和移动端设备  
- **实时天气数据**: 支持多个预定义城市及自定义城市搜索
- **美观的动画效果**: 流畅的交互体验和视觉反馈
- **缓存机制**: 智能缓存减少重复请求
- **错误处理**: 友好的错误提示和重试机制

## 🛠️ 技术栈

- **前端框架**: React 17
- **样式方案**: Styled Components
- **HTTP 客户端**: Axios
- **构建工具**: Vite (主版本) / CDN (独立版本)
- **测试框架**: Jest + React Testing Library

## 📂 项目结构

```
weather-app/
├── public/                 # 静态资源
├── src/                   # 源代码
│   ├── components/        # React组件
│   │   ├── WeatherDisplay.jsx    # 主展示组件
│   │   ├── TemperatureCard.jsx   # 温度卡片
│   │   ├── HumidityCard.jsx      # 湿度卡片
│   │   ├── LocationSelector.jsx  # 位置选择器
│   │   ├── LoadingSpinner.jsx    # 加载动画
│   │   └── ErrorMessage.jsx      # 错误信息
│   ├── services/          # API服务
│   │   └── weatherService.js     # 天气数据服务
│   ├── __tests__/         # 测试文件
│   ├── WeatherApp.jsx     # 根组件
│   ├── main.jsx          # 应用入口
│   └── index.css         # 全局样式
├── index-standalone.html  # 独立运行版本
├── package.json          # 项目配置
└── README.md            # 项目说明
```

## 🎯 组件设计

### 组件层次结构
```
WeatherApp (根组件)
├── LocationSelector (位置选择)
├── LoadingSpinner (加载状态)
├── ErrorMessage (错误处理)
└── WeatherDisplay (天气展示)
    ├── TemperatureCard (温度卡片)
    └── HumidityCard (湿度卡片)
```

### 状态管理
- **weatherData**: 天气信息 (温度、湿度、位置、更新时间)
- **isLoading**: 加载状态
- **error**: 错误信息
- **selectedLocation**: 选中的城市

## 🎨 设计特色

### 视觉设计
- **渐变背景**: 蓝色渐变营造天空感
- **玻璃态效果**: 半透明卡片与模糊背景
- **图标语义化**: 温湿度状态直观显示
- **动画交互**: 悬停效果和页面过渡

### 响应式布局
- **桌面端**: 横向排列的卡片布局
- **移动端**: 纵向堆叠的紧凑布局
- **自适应字体**: 根据屏幕尺寸调整字体大小

## 🚀 快速开始

### 方法一：独立版本 (推荐)
```bash
# 克隆项目
cd weather-app

# 启动HTTP服务器
python3 -m http.server 9000

# 访问应用
open http://localhost:9000/index-standalone.html
```

### 方法二：开发环境
```bash
# 安装依赖
npm install

# 启动开发服务器 (需要Node.js 16+)
npm run dev
```

## 🧪 测试

```bash
# 运行单元测试
npm test

# 运行测试覆盖率
npm test -- --coverage
```

## 📱 功能展示

### 主要功能
1. **城市选择**: 支持预定义城市快速选择
2. **自定义搜索**: 输入任意城市名称搜索
3. **温度显示**: 带状态提示的温度信息
4. **湿度显示**: 带进度条的湿度信息
5. **实时更新**: 显示最后更新时间
6. **错误处理**: 网络错误和重试机制

### 支持的城市
- 预定义城市: 北京、上海、广州、深圳、杭州、南京、成都、重庆、武汉、西安、天津、青岛、大连、厦门、苏州
- 自定义城市: 支持任意城市名称搜索

## 🔧 API 集成

### 天气服务特性
- **模拟数据**: 内置15个城市的天气数据
- **随机生成**: 未知城市自动生成合理的天气数据
- **缓存机制**: 5分钟缓存避免重复请求
- **错误模拟**: 随机错误帮助测试错误处理

### 扩展真实API
```javascript
// 在weatherService.js中配置真实API
const API_CONFIG = {
  BASE_URL: 'https://api.openweathermap.org/data/2.5',
  API_KEY: 'your_api_key_here',
  // ...
};
```

## 📊 性能优化

- **React.memo**: 防止不必要的组件重渲染
- **useCallback**: 优化事件处理函数
- **代码分割**: 按需加载组件
- **缓存策略**: 智能缓存减少API调用

## 🎯 测试策略

### 测试覆盖
- **组件渲染测试**: 验证组件正确渲染
- **交互测试**: 验证用户操作响应
- **API测试**: 验证数据获取逻辑
- **错误处理测试**: 验证异常情况处理

### 测试工具
- Jest: 测试框架
- React Testing Library: 组件测试
- @testing-library/jest-dom: DOM断言

## 🔮 未来规划

- [ ] 添加更多天气信息 (风力、气压等)
- [ ] 支持天气预报功能
- [ ] 添加地图集成
- [ ] 支持多语言
- [ ] 添加主题切换
- [ ] PWA支持

## 📄 开源协议

MIT License

## 👥 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

---

**注意**: 当前版本使用模拟数据，如需接入真实天气API，请配置相应的API密钥。