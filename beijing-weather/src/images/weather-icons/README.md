# 天气图标说明

## 图标文件结构

本目录包含天气显示页面所需的天气图标文件。图标按照天气状况分类，支持多种天气条件的可视化展示。

## 图标命名规范

### 基本天气状况
- `sunny.png` - 晴天
- `cloudy.png` - 多云
- `few-clouds.png` - 少云
- `partly-cloudy.png` - 晴间多云
- `overcast.png` - 阴天
- `clear-night.png` - 晴朗夜间
- `cloudy-night.png` - 多云夜间
- `few-clouds-night.png` - 少云夜间
- `partly-cloudy-night.png` - 晴间多云夜间

### 降雨天气
- `shower-rain.png` - 阵雨
- `heavy-shower-rain.png` - 强阵雨
- `light-rain.png` - 小雨
- `moderate-rain.png` - 中雨
- `heavy-rain.png` - 大雨
- `extreme-rain.png` - 极端降雨
- `drizzle.png` - 毛毛雨
- `heavy-storm.png` - 暴雨
- `severe-storm.png` - 大暴雨
- `extreme-storm.png` - 特大暴雨
- `freezing-rain.png` - 冻雨

### 雷雨天气
- `thunderstorm.png` - 雷阵雨
- `heavy-thunderstorm.png` - 强雷阵雨
- `thunderstorm-with-hail.png` - 雷阵雨伴有冰雹

### 降雪天气
- `light-snow.png` - 小雪
- `moderate-snow.png` - 中雪
- `heavy-snow.png` - 大雪
- `snowstorm.png` - 暴雪
- `sleet.png` - 雨夹雪
- `rain-and-snow.png` - 雨雪天气
- `shower-snow.png` - 阵雪
- `snow-flurry.png` - 阵雪
- `light-to-moderate-snow.png` - 小到中雪
- `moderate-to-heavy-snow.png` - 中到大雪
- `heavy-snow-to-snowstorm.png` - 大到暴雪

### 特殊天气
- `mist.png` - 薄雾
- `fog.png` - 雾
- `haze.png` - 霾
- `sand.png` - 扬沙
- `dust.png` - 浮尘
- `duststorm.png` - 沙尘暴
- `sandstorm.png` - 强沙尘暴
- `dense-fog.png` - 浓雾
- `severe-haze.png` - 强浓雾
- `moderate-haze.png` - 中度霾
- `heavy-haze.png` - 重度霾
- `heavy-fog.png` - 大雾
- `extra-heavy-fog.png` - 特强浓雾

### 温度相关
- `hot.png` - 高温
- `cold.png` - 低温

### 默认图标
- `unknown.png` - 未知天气状况

## 图标规格要求

### 文件格式
- 推荐使用PNG格式，支持透明背景
- 文件大小控制在50KB以内
- 支持SVG格式用于矢量图标

### 尺寸规格
- 推荐尺寸：128x128像素
- 最小尺寸：64x64像素
- 最大尺寸：256x256像素
- 支持高DPI显示（@2x, @3x）

### 设计要求
- 图标风格保持一致
- 使用清晰易识别的符号
- 颜色搭配符合天气特征
- 支持深色和浅色主题

## 图标来源建议

### 免费图标资源
1. **Weather Icons** - https://erikflowers.github.io/weather-icons/
2. **Feather Icons** - https://feathericons.com/
3. **Heroicons** - https://heroicons.com/
4. **Ionicons** - https://ionicons.com/
5. **Material Design Icons** - https://materialdesignicons.com/

### 自定义图标
- 可以使用设计工具（如Figma、Sketch）创建
- 遵循Material Design或类似的设计规范
- 确保图标在不同尺寸下的清晰度

## 使用方法

图标通过 `WeatherAPI.getWeatherIconUrl()` 方法调用：

```javascript
// 获取天气图标URL
const iconUrl = WeatherAPI.getWeatherIconUrl('100'); // 和风天气代码
const iconUrl = WeatherAPI.getWeatherIconUrl('01d'); // OpenWeatherMap代码
```

## 注意事项

1. **版权问题**：确保使用的图标具有合适的使用许可
2. **加载性能**：优化图标文件大小，提高页面加载速度
3. **兼容性**：确保图标在不同浏览器中正常显示
4. **无障碍**：为图标添加合适的alt文本描述

## 扩展图标

如需添加新的天气图标：

1. 在此目录添加图标文件
2. 更新 `config.js` 中的 `WEATHER_ICONS` 映射
3. 确保图标命名遵循现有规范
4. 测试图标在不同设备上的显示效果