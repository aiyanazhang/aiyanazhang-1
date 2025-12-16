# Gold Price Display - Implementation Spec

## Overview
Create a single-file HTML page that displays today's gold price with auto-refresh capability, using the gold-api.com public API.

## Requirements
- Display current gold price in multiple formats (USD/oz, CNY/oz, USD/g, CNY/g, CNY/kg)
- Auto-refresh every 5 minutes
- Manual refresh button
- Bilingual UI (English/Chinese)
- Single self-contained HTML file
- No authentication required
- Cache mechanism for offline resilience

## API Selection
**Endpoint**: `https://api.gold-api.com/price/XAU`

**Response format**:
```json
{
  "name": "Gold",
  "price": 4295.600098,
  "symbol": "XAU",
  "updatedAt": "2025-12-16T02:57:09Z",
  "updatedAtReadable": "a few seconds ago"
}
```

**Rationale**: No authentication required, simple REST endpoint, real-time data, free to use.

## File Structure
Create new file: `/Users/zay/aiyanazhang-1/gold-price.html`

## Implementation Details

### 1. HTML Structure
- Header with title "🪙 Today's Gold Price / 今日金价"
- Refresh button with rotation animation
- Current timestamp display
- Main card container with:
  - Loading state (spinner + message)
  - Error state (message + retry button)
  - Success state (price display)
- Primary price display (large, prominent)
- Details grid (2x2 layout):
  - CNY per oz / 人民币/盎司
  - USD per gram / 美元/克
  - CNY per gram / 人民币/克
  - CNY per kg / 人民币/千克
- Footer with data source attribution

### 2. CSS Styling
**Pattern reference**: `/Users/zay/aiyanazhang-1/weather.html:14-159`

- Gradient background: `linear-gradient(135deg, #FFD700 0%, #DAA520 100%)` (gold theme)
- Card container: `max-width: 600px`, `border-radius: 20px`, glassmorphism effect
- Primary price: `60px` font size, `#DAA520` color, bold weight
- Grid layout: 2 columns on desktop, 1 column on mobile
- Loading spinner with CSS animation
- Hover effects on buttons
- Smooth fade-in transitions

**Responsive breakpoint**: `@media (max-width: 768px)`

### 3. JavaScript Functionality

#### Configuration
- API endpoint: `https://api.gold-api.com/price/XAU`
- Refresh interval: 5 minutes (300000ms)
- Cache expiry: 10 minutes
- USD to CNY rate: 7.2 (approximate)
- Request timeout: 10 seconds
- Troy ounce to gram conversion: 31.1035

#### Core Functions

**`fetchGoldPrice()`**
- Pattern reference: `/Users/zay/aiyanazhang-1/beijing-weather/src/js/weather-api.js:36-54`
- Fetch API with timeout wrapper
- Retry logic (3 attempts with exponential backoff)
- Validate response structure
- Return parsed JSON

**`processGoldData(apiResponse)`**
- Extract price from API response
- Calculate conversions:
  - USD/oz → CNY/oz: `price * 7.2`
  - USD/oz → USD/g: `price / 31.1035`
  - USD/g → CNY/g: `(price / 31.1035) * 7.2`
  - CNY/g → CNY/kg: `((price / 31.1035) * 7.2) * 1000`
- Format numbers with 2 decimal places
- Add thousand separators
- Parse timestamp to Beijing timezone

**`updateUI(goldData)`**
- Pattern reference: `/Users/zay/aiyanazhang-1/weather.html:238-248`
- Hide loading state
- Populate all price fields
- Update timestamp display
- Show success state with fade-in animation
- Update "next refresh" countdown

**`showLoading()`**
- Display loading spinner
- Show bilingual loading message
- Hide error and success states

**`showError(message)`**
- Pattern reference: `/Users/zay/aiyanazhang-1/weather.html:232`
- Display error message (bilingual)
- Show retry button
- Hide loading and success states

**`handleRefresh()`**
- Trigger manual refresh
- Add button rotation animation
- Call `fetchGoldPrice()`
- Debounce to prevent spam clicks

**`startAutoRefresh()`**
- Set interval to refresh every 5 minutes
- Update countdown timer every second
- Clear interval on page unload

**Cache Management** (localStorage)
- Pattern reference: `/Users/zay/aiyanazhang-1/beijing-weather/src/js/weather-api.js:344-378`
- Cache key: `gold_price_cache`
- Save with timestamp on successful fetch
- Check cache validity (10-minute expiry)
- Fall back to cache on API failure
- Display cache warning when using stale data

#### Error Handling
- Network failures: Show retry button
- API unavailable: Fall back to cached data
- Invalid response: Log error and show user message
- Timeout: Abort request after 10 seconds

### 4. Auto-Refresh Implementation
- Initial load: Fetch immediately on page load
- Interval: Refresh every 5 minutes
- Countdown display: "Next update in 4:32"
- Manual refresh: Reset countdown timer
- Page visibility: Pause when tab hidden (optional enhancement)

### 5. Bilingual Labels

| Element | English | Chinese |
|---------|---------|---------|
| Page title | Today's Gold Price | 今日金价 |
| Refresh button | Refresh | 刷新 |
| Loading | Loading gold price data... | 正在加载金价数据... |
| Error | Failed to fetch gold price | 获取金价失败 |
| Retry button | Retry | 重试 |
| Primary label | Current Price | 当前价格 |
| Unit | per troy oz | 每金衡盎司 |
| Last updated | Last Updated | 最后更新 |
| Next update | Next Update | 下次更新 |
| Data source | Data source: gold-api.com | 数据来源: gold-api.com |
| Cache warning | Using cached data (API unavailable) | 使用缓存数据（API不可用） |

### 6. Price Display Format Examples
- USD/oz: `$4,295.60`
- CNY/oz: `¥30,928.32`
- USD/g: `$138.08`
- CNY/g: `¥994.18`
- CNY/kg: `¥994,180.00`

### 7. Edge Cases & Error Handling
1. **API unavailable**: Fall back to cached data, show warning
2. **Invalid response**: Validate price is positive number, show error if invalid
3. **Network timeout**: Abort after 10s, show retry option
4. **localStorage full**: Continue without cache, log warning
5. **Price volatility**: Display timestamp prominently, allow manual refresh

## Implementation Steps

1. **Create file structure** (5 min)
   - Create `/Users/zay/aiyanazhang-1/gold-price.html`
   - Set up HTML5 boilerplate
   - Add meta tags and charset

2. **HTML markup** (15 min)
   - Header section with title and controls
   - Main card container
   - Loading/error/success state sections
   - Footer with attribution

3. **CSS styling** (30 min)
   - Gold-themed gradient background
   - Card styling with glassmorphism
   - Grid layout for price details
   - Loading spinner animation
   - Button hover effects
   - Responsive media queries

4. **JavaScript configuration** (10 min)
   - Define constants (API URL, intervals, conversion rates)
   - Set up configuration object

5. **API integration** (30 min)
   - Implement `fetchGoldPrice()` with timeout
   - Add retry logic with exponential backoff
   - Validate response structure

6. **Data processing** (20 min)
   - Implement `processGoldData()`
   - Calculate all price conversions
   - Format numbers with separators and decimals

7. **UI rendering** (30 min)
   - Implement state management (loading/error/success)
   - Create `updateUI()` function
   - Add fade-in animations
   - Wire up all DOM elements

8. **Cache implementation** (20 min)
   - localStorage get/set functions
   - Cache validation logic
   - Fallback to cache on error

9. **Auto-refresh** (15 min)
   - Set up interval timer
   - Implement countdown display
   - Handle manual refresh button

10. **Testing & polish** (30 min)
    - Test with live API
    - Test error scenarios (disconnect network)
    - Verify responsive layout
    - Cross-browser testing

**Total estimated time**: 3 hours

## Critical Reference Files
- `/Users/zay/aiyanazhang-1/weather.html` - Single-file structure, gradient styling, API integration pattern
- `/Users/zay/aiyanazhang-1/beijing-weather/src/js/weather-api.js` - Retry logic, cache management, data transformation patterns

## Success Criteria
- ✓ Displays current gold price in USD/oz prominently
- ✓ Shows conversions for CNY and different units
- ✓ Auto-refreshes every 5 minutes
- ✓ Manual refresh button works
- ✓ Error handling with user feedback
- ✓ Cache fallback for offline resilience
- ✓ Bilingual interface (English/Chinese)
- ✓ Mobile-responsive design
- ✓ No external dependencies
- ✓ No authentication required
