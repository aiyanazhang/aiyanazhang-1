# Hello World系统使用示例

本文档提供了Hello World Python脚本系统的详细使用示例，帮助用户快速上手并充分利用系统的各种功能。

## 基础使用示例

### 1. 最简单的使用

```bash
# 显示默认的Hello World消息
python main.py
```

输出：
```
Hello, World!
```

### 2. 个性化问候

```bash
# 指定用户名
python main.py --name "张三"
```

输出：
```
Hello, 张三!
```

### 3. 中文问候

```bash
# 使用中文
python main.py --name "张三" --language zh
```

输出：
```
你好，张三！
```

### 4. 详细模式

```bash
# 显示详细信息
python main.py --name "TestUser" --verbose
```

输出：
```
Hello, TestUser!
Welcome to the Hello World System.
Current time: 2024-01-01 12:00:00

=== Details ===
User name: TestUser
Language: en
Timestamp: 2024-01-01 12:00:00
Template: verbose
```

## 输出格式示例

### 1. JSON格式输出

```bash
python main.py --name "API用户" --language zh --format json
```

输出：
```json
{
  "greeting": {
    "message": "你好，API用户！",
    "metadata": {
      "name": "API用户",
      "language": "zh",
      "timestamp": "2024年01月01日 12:00:00",
      "verbose": false,
      "template_used": "basic"
    },
    "system_info": {
      "version": "1.0.0",
      "format": "json",
      "generated_at": "2024-01-01T12:00:00.000000"
    }
  }
}
```

### 2. XML格式输出

```bash
python main.py --name "XML用户" --format xml --verbose
```

输出：
```xml
<?xml version="1.0" ?>
<greeting version="1.0.0" format="xml" generated_at="2024-01-01T12:00:00.000000">
  <message>Hello, XML用户!
Welcome to the Hello World System.
Current time: 2024-01-01 12:00:00</message>
  <metadata>
    <name>XML用户</name>
    <language>en</language>
    <timestamp>2024-01-01 12:00:00</timestamp>
    <verbose>true</verbose>
    <template_used>verbose</template_used>
  </metadata>
</greeting>
```

## 配置文件使用示例

### 1. 创建自定义配置文件

创建 `my-config.json` 文件：

```json
{
  "default_language": "zh",
  "default_format": "json",
  "enable_colors": true,
  "verbose": true,
  "greeting": {
    "add_emoji": true,
    "decoration_style": "box"
  }
}
```

使用自定义配置：

```bash
python main.py --config my-config.json --name "配置用户"
```

### 2. 不同环境的配置示例

#### 开发环境配置 (dev-config.json)
```json
{
  "default_language": "en",
  "log_level": "DEBUG",
  "verbose": true,
  "enable_colors": true,
  "output": {
    "show_metadata": true
  }
}
```

#### 生产环境配置 (prod-config.json)
```json
{
  "default_language": "zh",
  "log_level": "WARNING",
  "verbose": false,
  "enable_colors": false,
  "output": {
    "show_metadata": false
  }
}
```

## 高级使用示例

### 1. 批量处理示例

创建批处理脚本 `batch_greetings.sh`：

```bash
#!/bin/bash

# 定义用户列表
users=("张三" "李四" "王五" "赵六")

# 为每个用户生成问候
for user in "${users[@]}"; do
    echo "Processing: $user"
    python main.py --name "$user" --language zh --format json > "greeting_${user}.json"
    echo "Generated: greeting_${user}.json"
done

echo "All greetings generated!"
```

### 2. 国际化示例

为不同地区的用户生成问候：

```bash
# 英文用户
python main.py --name "John Smith" --language en --format text

# 中文用户
python main.py --name "张伟" --language zh --format text

# 带时区的详细信息
python main.py --name "Global User" --verbose --format json
```

### 3. 集成到其他系统

#### Python脚本集成示例

```python
#!/usr/bin/env python3
import subprocess
import json

def generate_greeting(name, language='en', format_type='json'):
    """生成问候消息"""
    cmd = [
        'python', 'main.py',
        '--name', name,
        '--language', language,
        '--format', format_type
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if format_type == 'json':
        return json.loads(result.stdout)
    else:
        return result.stdout.strip()

# 使用示例
user_greeting = generate_greeting("API用户", "zh", "json")
print(f"问候消息: {user_greeting['greeting']['message']}")
```

#### Web API集成示例

```python
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/greeting', methods=['GET'])
def get_greeting():
    name = request.args.get('name', 'World')
    language = request.args.get('language', 'en')
    
    cmd = [
        'python', 'main.py',
        '--name', name,
        '--language', language,
        '--format', 'json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return jsonify({'error': 'Failed to generate greeting'}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## 错误处理示例

### 1. 无效参数处理

```bash
# 无效的语言代码
python main.py --language invalid
```

输出：
```
错误: 参数值错误: invalid choice: 'invalid' (choose from 'en', 'zh')

使用 --help 查看详细使用说明
```

### 2. 配置文件错误处理

```bash
# 使用不存在的配置文件
python main.py --config nonexistent.json
```

输出：
```
错误: 参数值错误: 配置文件不存在: nonexistent.json

使用 --help 查看详细使用说明
```

### 3. 名称长度限制示例

```bash
# 过长的用户名
python main.py --name "这是一个非常非常非常非常非常非常非常非常非常非常非常非常长的用户名字"
```

输出（会被截断）：
```
你好，这是一个非常非常非常非常非常非常非常非常非常非常非常非常长的用...！
```

## 性能测试示例

### 1. 基准测试脚本

```bash
#!/bin/bash

echo "性能测试开始..."

# 测试不同格式的性能
for format in text json xml; do
    echo "测试 $format 格式..."
    time for i in {1..100}; do
        python main.py --name "TestUser$i" --format $format > /dev/null
    done
done

echo "性能测试完成"
```

### 2. 内存使用监控

```python
import psutil
import subprocess
import time

def monitor_memory_usage():
    """监控内存使用情况"""
    process = subprocess.Popen([
        'python', 'main.py', 
        '--name', 'MemoryTest', 
        '--verbose'
    ])
    
    # 监控进程
    p = psutil.Process(process.pid)
    max_memory = 0
    
    while process.poll() is None:
        try:
            memory_info = p.memory_info()
            current_memory = memory_info.rss / 1024 / 1024  # MB
            max_memory = max(max_memory, current_memory)
            time.sleep(0.01)
        except psutil.NoSuchProcess:
            break
    
    print(f"最大内存使用: {max_memory:.2f} MB")

monitor_memory_usage()
```

## 自动化测试示例

### 1. 功能验证脚本

```bash
#!/bin/bash

echo "开始功能验证测试..."

# 测试基本功能
test_basic() {
    result=$(python main.py 2>&1)
    if [[ $result == *"Hello, World!"* ]]; then
        echo "✓ 基本功能测试通过"
    else
        echo "✗ 基本功能测试失败"
        return 1
    fi
}

# 测试中文支持
test_chinese() {
    result=$(python main.py --name "测试" --language zh 2>&1)
    if [[ $result == *"你好，测试！"* ]]; then
        echo "✓ 中文支持测试通过"
    else
        echo "✗ 中文支持测试失败"
        return 1
    fi
}

# 测试JSON输出
test_json() {
    result=$(python main.py --format json 2>&1)
    if [[ $result == *"\"greeting\""* ]]; then
        echo "✓ JSON输出测试通过"
    else
        echo "✗ JSON输出测试失败"
        return 1
    fi
}

# 执行所有测试
test_basic
test_chinese
test_json

echo "功能验证测试完成"
```

### 2. 回归测试示例

```python
#!/usr/bin/env python3
import subprocess
import json
import sys

def run_test(name, cmd, expected_keywords):
    """运行单个测试"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ {name}: 命令执行失败")
            return False
        
        output = result.stdout
        for keyword in expected_keywords:
            if keyword not in output:
                print(f"✗ {name}: 缺少关键词 '{keyword}'")
                return False
        
        print(f"✓ {name}: 测试通过")
        return True
        
    except Exception as e:
        print(f"✗ {name}: 异常 {e}")
        return False

def main():
    """主测试函数"""
    tests = [
        {
            'name': '基本问候测试',
            'cmd': ['python', 'main.py'],
            'expected': ['Hello, World!']
        },
        {
            'name': '个性化问候测试',
            'cmd': ['python', 'main.py', '--name', 'TestUser'],
            'expected': ['Hello, TestUser!']
        },
        {
            'name': '中文问候测试',
            'cmd': ['python', 'main.py', '--name', '测试用户', '--language', 'zh'],
            'expected': ['你好，测试用户！']
        },
        {
            'name': 'JSON格式测试',
            'cmd': ['python', 'main.py', '--format', 'json'],
            'expected': ['"greeting"', '"message"']
        },
        {
            'name': '详细模式测试',
            'cmd': ['python', 'main.py', '--verbose'],
            'expected': ['Hello, World!', 'Welcome to']
        }
    ]
    
    passed = 0
    total = len(tests)
    
    print("开始回归测试...\n")
    
    for test in tests:
        if run_test(test['name'], test['cmd'], test['expected']):
            passed += 1
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败！")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

## 故障排除示例

### 1. 常见问题诊断

```bash
#!/bin/bash

echo "Hello World系统诊断工具"
echo "========================"

# 检查Python版本
echo "检查Python版本..."
python_version=$(python --version 2>&1)
echo "Python版本: $python_version"

# 检查文件结构
echo -e "\n检查文件结构..."
required_files=("main.py" "src/greeting.py" "src/args_parser.py" "src/output.py" "src/config.py")

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✓ $file 存在"
    else
        echo "✗ $file 缺失"
    fi
done

# 检查配置文件
echo -e "\n检查配置文件..."
if [[ -f "config/config.json" ]]; then
    echo "✓ 默认配置文件存在"
    # 验证JSON格式
    if python -m json.tool config/config.json > /dev/null 2>&1; then
        echo "✓ 配置文件格式正确"
    else
        echo "✗ 配置文件格式错误"
    fi
else
    echo "! 默认配置文件不存在（将使用内置默认值）"
fi

# 运行基本测试
echo -e "\n运行基本测试..."
if python main.py > /dev/null 2>&1; then
    echo "✓ 基本功能正常"
else
    echo "✗ 基本功能异常"
    echo "错误信息:"
    python main.py 2>&1
fi

echo -e "\n诊断完成"
```

### 2. 调试模式示例

```bash
# 启用详细日志
export PYTHONPATH="${PYTHONPATH}:./src"
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)

from main import HelloWorldApp
app = HelloWorldApp()
app.run(['--name', 'DebugUser', '--verbose'])
"
```

这些示例展示了Hello World系统的各种使用场景，从简单的命令行使用到复杂的集成应用，帮助用户充分了解和使用系统的所有功能。