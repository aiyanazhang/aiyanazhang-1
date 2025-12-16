# 汇率转换工具页面实现规范

## 一、需求概述

为静态 HTML5 工具箱应用增加一个汇率转换页面,支持常用货币之间的单向转换,使用免费 API,并遵循现有项目的设计模式和代码风格。

## 二、技术栈

- **前端**: 纯 HTML5 + CSS3 + JavaScript ES6+
- **API**: exchangerate-api.com 免费版(无需 API Key)
- **数据缓存**: localStorage
- **部署**: 静态文件托管

## 三、文件操作清单

### 需要修改的文件

**`/data/workspace/aiyanazhang-1/index.html`** (第159-163行)
- 将"汇率换算"从 `<div class="tool-card coming-soon">` 改为可点击链接
- 修改为: `<a href="tools/finance/exchange-rate.html" class="tool-card">`

### 需要创建的文件

**`/data/workspace/aiyanazhang-1/tools/finance/exchange-rate.html`**
- 完整的单文件 HTML 应用(包含内嵌的 CSS 和 JavaScript)

## 四、核心设计

### 4.1 支持的货币列表

支持以下 12 种常用货币:

| 货币代码 | 货币名称 | 符号 | 国旗 |
|---------|---------|------|------|
| USD | 美元 US Dollar | $ | 🇺🇸 |
| CNY | 人民币 Chinese Yuan | ¥ | 🇨🇳 |
| EUR | 欧元 Euro | € | 🇪🇺 |
| GBP | 英镑 British Pound | £ | 🇬🇧 |
| JPY | 日元 Japanese Yen | ¥ | 🇯🇵 |
| HKD | 港币 Hong Kong Dollar | HK$ | 🇭🇰 |
| AUD | 澳元 Australian Dollar | A$ | 🇦🇺 |
| CAD | 加元 Canadian Dollar | C$ | 🇨🇦 |
| SGD | 新加坡元 Singapore Dollar | S$ | 🇸🇬 |
| CHF | 瑞士法郎 Swiss Franc | CHF | 🇨🇭 |
| KRW | 韩元 South Korean Won | ₩ | 🇰🇷 |
| THB | 泰铢 Thai Baht | ฿ | 🇹🇭 |

### 4.2 API 集成

**API URL**: `https://api.exchangerate-api.com/v4/latest/USD`

**响应结构**:
```json
{
  "base": "USD",
  "date": "2025-12-16",
  "rates": {
    "USD": 1,
    "CNY": 7.06,
    "EUR": 0.851,
    ...
  }
}
```

**错误处理策略**:
- 超时控制: 10秒
- 重试机制: 最多3次,指数退避(1s, 2s, 4s)
- 降级方案: API 失败时使用 localStorage 缓存数据(24小时有效期)

### 4.3 配置对象

```javascript
const CONFIG = {
  API_BASE_URL: 'https://api.exchangerate-api.com/v4/latest/',
  DEFAULT_BASE_CURRENCY: 'USD',
  CACHE_EXPIRY: 86400000,  // 24小时
  REQUEST_TIMEOUT: 10000,   // 10秒
  MAX_RETRIES: 3,
  CACHE_KEY: 'exchange_rate_cache'
};
```

### 4.4 核心函数列表

**数据获取层**:
1. `fetchWithTimeout(url, timeout)` - 带超时控制的 Fetch 封装
2. `fetchExchangeRates(baseCurrency, retryCount)` - 获取汇率数据(带重试)
3. `saveToCache(data)` - 保存到 localStorage
4. `getFromCache()` - 从 localStorage 读取缓存

**数据处理层**:
5. `processRatesData(apiResponse)` - 处理 API 响应数据
6. `calculateConversion(amount, fromCurrency, toCurrency)` - 交叉汇率计算
7. `formatAmount(value, currencyCode)` - 金额格式化(千分位+小数位)

**UI 交互层**:
8. `initCurrencySelectors()` - 初始化货币选择下拉框
9. `handleConvert()` - 处理转换按钮点击事件
10. `updateResultDisplay(result)` - 更新结果显示区域
11. `showState(state)` - 切换 loading/error/success 状态
12. `updateRateInfo()` - 更新汇率信息和更新时间

**生命周期管理**:
13. `loadExchangeRates()` - 页面加载时获取汇率数据
14. `handleRefresh()` - 手动刷新汇率数据

### 4.5 汇率计算算法

由于 API 返回的是相对 USD 的汇率,需要实现交叉汇率计算:

```
公式: targetAmount = sourceAmount × (targetRate / sourceRate)

示例: 100 CNY → EUR
- sourceRate (CNY) = 7.06
- targetRate (EUR) = 0.851
- 结果 = 100 × (0.851 / 7.06) = 12.05 EUR
```

**特殊情况处理**:
- 相同货币转换: 直接返回原金额
- 金额为0或空: 提示"请输入金额"
- 精度控制: 保留2位小数(日元和韩元保留0位)

## 五、UI/UX 设计

### 5.1 页面结构

```
<body>
  <nav class="top-navbar">
    └─ 返回主页按钮 (🏠 返回主页)
  </nav>
  
  <div class="container">
    <div class="header">
      ├─ 页面标题 (💱 汇率换算)
      ├─ 副标题 (实时汇率数据,支持主流货币)
      └─ 刷新按钮
    </div>
    
    <div class="loading-state">旋转加载动画</div>
    
    <div class="error-state">错误信息 + 重试按钮</div>
    
    <div class="success-state">
      ├─ 缓存警告框 (条件显示)
      ├─ 转换器表单
      │   ├─ 金额输入框
      │   ├─ 源货币选择器
      │   ├─ 方向图标 (→)
      │   ├─ 目标货币选择器
      │   └─ 转换按钮
      └─ 结果展示区
          ├─ 转换结果
          └─ 当前汇率信息
    </div>
    
    <div class="footer">数据来源说明</div>
  </div>
</body>
```

### 5.2 样式主题

**主题色**: 货币绿色渐变
- 背景渐变: `linear-gradient(135deg, #10B981 0%, #059669 100%)`
- 主标题色: `#10B981`
- 转换按钮: `linear-gradient(135deg, #10B981, #059669)`
- 结果数值色: `#059669`

**关键元素样式**:
- 导航栏: 固定顶部,绿色半透明背景
- 主容器: 最大宽度 600px,白色卡片,圆角 20px
- 输入框: 默认边框 #D1D5DB,焦点时边框变为 #10B981
- 按钮: 悬停时轻微放大,点击时缩小

**响应式设计**:
- 桌面 (≥769px): 双列布局
- 移动 (≤768px): 单列布局,表单元素垂直排列

### 5.3 状态管理

三态切换机制:
- **loading**: 显示旋转加载动画
- **error**: 显示错误信息和重试按钮
- **success**: 显示转换表单和结果

使用 `.show` class 控制显示/隐藏,配合 `fadeIn` 动画。

## 六、实现步骤

### 步骤 1: 修改主页导航链接
**文件**: `/data/workspace/aiyanazhang-1/index.html`
**位置**: 第159-163行
**操作**: 
```html
<!-- 修改前 -->
<div class="tool-card coming-soon">
    <span class="tool-icon">💹</span>
    <div class="tool-title">汇率换算</div>
    <p class="tool-description">实时汇率查询与换算，支持多种主流货币</p>
</div>

<!-- 修改后 -->
<a href="tools/finance/exchange-rate.html" class="tool-card">
    <span class="tool-icon">💹</span>
    <div class="tool-title">汇率换算</div>
    <p class="tool-description">实时汇率查询与换算，支持多种主流货币</p>
</a>
```

### 步骤 2: 创建 exchange-rate.html 骨架
**参考文件**: `/data/workspace/aiyanazhang-1/tools/finance/gold-price.html`
**操作**:
- 复制 gold-price.html 作为模板
- 修改 `<title>` 为 "💱 汇率换算"
- 保留导航栏、footer、基础样式结构

### 步骤 3: 定义 CONFIG 配置对象
在 `<script>` 标签中定义配置对象,包含:
- API_BASE_URL
- SUPPORTED_CURRENCIES 数组(12种货币,每种包含 code/name/symbol/flag 属性)
- 缓存和超时配置

### 步骤 4: 实现数据获取层函数
实现以下函数(可从 gold-price.html 复用部分逻辑):
1. `fetchWithTimeout()` - 超时控制
2. `fetchExchangeRates()` - API 调用和重试
3. `saveToCache()` / `getFromCache()` - 缓存管理

### 步骤 5: 实现数据处理层函数
实现核心计算逻辑:
1. `calculateConversion()` - 交叉汇率计算公式: `amount × (targetRate / sourceRate)`
2. `formatAmount()` - 金额格式化(千分位 + 货币符号)
3. 数据验证和错误处理

### 步骤 6: 构建 HTML 表单结构
在 `<div class="success-state">` 中添加:
- 金额输入框: `<input type="number" id="amountInput">`
- 源货币选择器: `<select id="fromCurrency">`
- 目标货币选择器: `<select id="toCurrency">`
- 转换按钮: `<button onclick="handleConvert()">`
- 结果显示区: `<div id="resultDisplay">`

### 步骤 7: 实现 UI 交互层函数
1. `initCurrencySelectors()` - 遍历 SUPPORTED_CURRENCIES 生成 `<option>` 元素
2. `handleConvert()` - 读取输入 → 验证 → 计算 → 更新结果
3. `updateResultDisplay()` - 渲染转换结果和汇率信息
4. `showState()` - 状态切换控制

### 步骤 8: 编写 CSS 样式
**重点样式**:
- 修改背景渐变为绿色主题
- 设计转换器表单布局(Flexbox)
- 设计结果显示卡片样式
- 添加输入框 focus 高亮效果
- 移动端响应式断点(@media max-width: 768px)

### 步骤 9: 实现生命周期管理
1. `window.addEventListener('load')` - 调用 `loadExchangeRates()` 和 `initCurrencySelectors()`
2. `loadExchangeRates()` - 显示 loading → 获取 API → 更新 UI
3. `handleRefresh()` - 刷新按钮旋转动画 → 重新加载数据

### 步骤 10: 测试和验证
测试场景:
- API 调用正常情况
- API 失败 + 有缓存
- API 失败 + 无缓存
- 输入验证(负数/空值/非数字)
- 相同货币转换
- 移动端布局

## 七、关键技术要点

### 7.1 输入验证
```javascript
function validateAmount(input) {
  const value = parseFloat(input);
  if (isNaN(value)) return { valid: false, error: '请输入有效数字' };
  if (value < 0) return { valid: false, error: '金额不能为负数' };
  if (value === 0) return { valid: false, error: '请输入大于0的金额' };
  return { valid: true, value };
}
```

### 7.2 防抖处理
对转换按钮添加防抖,避免快速多次点击:
```javascript
let isConverting = false;
if (isConverting) return;
isConverting = true;
// 执行转换逻辑
setTimeout(() => isConverting = false, 500);
```

### 7.3 缓存策略
- 缓存时长: 24小时(汇率数据每日更新一次)
- 缓存内容: `{ base: 'USD', rates: {...}, timestamp: ..., date: '...' }`
- 缓存验证: 检查 timestamp 是否超过 CACHE_EXPIRY
- 降级策略: API 失败时显示缓存警告但允许继续使用

## 八、参考文件

**主要参考**: `/data/workspace/aiyanazhang-1/tools/finance/gold-price.html`
- 复用: 页面结构、状态管理、缓存机制、错误处理、重试逻辑
- 差异: 金价工具是只读展示,汇率工具是交互式输入输出

## 九、性能优化

1. 减少 DOM 操作: 使用 DocumentFragment 批量插入选择器 options
2. 防抖节流: 转换按钮防抖 500ms
3. 缓存复用: localStorage 缓存避免重复 API 调用
4. CSS 动画: 使用 transform 代替 position 变化

## 十、验收标准

- [ ] 主页"汇率换算"卡片可点击,链接到新页面
- [ ] 页面成功加载并显示转换表单
- [ ] 货币选择器包含12种常用货币
- [ ] 输入金额后点击转换按钮,正确显示转换结果
- [ ] 显示当前汇率信息(如: 1 USD = 7.06 CNY)
- [ ] API 失败时使用缓存数据并显示警告
- [ ] 移动端布局正常,表单元素垂直排列
- [ ] 页面样式与金价工具保持一致的设计风格
