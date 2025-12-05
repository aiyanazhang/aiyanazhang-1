# 微信小程序随机菜单生成器 - 后端

## 项目简介

这是一个基于 Flask 的后端 API 服务，为微信小程序提供随机菜单生成功能。支持三菜一汤的菜单生成、自定义菜品添加和收藏功能。

## 功能特性

- 🍽️ 菜品管理（预设菜品库 + 自定义添加）
- 🎲 随机生成三菜一汤菜单
- ⭐ 收藏喜欢的菜单
- 💾 SQLite 数据库存储

## 技术栈

- Python 3.8+
- Flask 3.0.0
- Flask-CORS 4.0.0
- SQLite3

## 安装部署

### 1. 安装依赖

```bash
cd meal-menu-backend
pip install -r requirements.txt
```

### 2. 初始化数据库

运行以下命令初始化数据库并导入预设菜品：

```bash
python init_db.py
```

这将创建 `menu.db` 数据库文件，并导入 30 道预设菜品和 12 种汤品。

### 3. 启动服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:5000` 启动。

## API 接口文档

### 1. 获取所有菜品

**请求：**
```
GET /api/dishes
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "宫保鸡丁",
      "category": "dish",
      "is_preset": 1,
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

### 2. 添加自定义菜品

**请求：**
```
POST /api/dishes
Content-Type: application/json

{
  "name": "自定义菜品",
  "category": "dish"  // 或 "soup"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "id": 43,
    "name": "自定义菜品",
    "category": "dish"
  }
}
```

### 3. 随机生成菜单

**请求：**
```
GET /api/generate-menu
```

**响应：**
```json
{
  "success": true,
  "data": {
    "dishes": [
      {"id": 1, "name": "宫保鸡丁"},
      {"id": 5, "name": "糖醋排骨"},
      {"id": 8, "name": "西红柿炒鸡蛋"}
    ],
    "soup": {
      "id": 31,
      "name": "紫菜蛋花汤"
    }
  }
}
```

### 4. 添加收藏

**请求：**
```
POST /api/favorites
Content-Type: application/json

{
  "menu": {
    "dishes": [...],
    "soup": {...}
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "id": 1
  }
}
```

### 5. 获取收藏列表

**请求：**
```
GET /api/favorites
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "menu_data": {...},
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

### 6. 删除收藏

**请求：**
```
DELETE /api/favorites/{id}
```

**响应：**
```json
{
  "success": true,
  "message": "删除成功"
}
```

## 数据库结构

### dishes 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 菜品名称 |
| category | TEXT | 分类（dish/soup） |
| is_preset | INTEGER | 是否预设（1/0） |
| created_at | TEXT | 创建时间 |

### favorites 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| menu_data | TEXT | 菜单JSON数据 |
| created_at | TEXT | 创建时间 |

## 配置说明

如果需要修改服务器地址或端口，请编辑 `app.py` 文件的最后一行：

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 生产环境部署建议

1. 使用 gunicorn 或 uwsgi 作为 WSGI 服务器
2. 配置 Nginx 作为反向代理
3. 关闭 Flask 的 debug 模式
4. 使用环境变量管理配置
5. 定期备份数据库文件

示例 gunicorn 启动命令：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 开发说明

- 预设菜品数据位于 `data/preset_dishes.json`
- 可以根据需要修改预设菜品
- 修改后重新运行 `python init_db.py` 导入数据（会清空现有数据）

## 常见问题

**Q: 数据库文件在哪里？**  
A: 运行 `init_db.py` 或 `app.py` 后，会在项目根目录生成 `menu.db` 文件。

**Q: 如何重置数据库？**  
A: 删除 `menu.db` 文件，然后重新运行 `python init_db.py`。

**Q: 如何添加更多预设菜品？**  
A: 编辑 `data/preset_dishes.json` 文件，添加新的菜品，然后重新运行 `python init_db.py`。

## 许可证

MIT License
