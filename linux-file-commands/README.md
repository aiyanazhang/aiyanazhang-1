# Linux文件操作命令查询工具

一个功能强大的Linux文件操作命令学习和查询工具，帮助用户快速查找、学习和使用各种Linux文件操作命令。

## 功能特性

- **完整的命令数据库**: 包含19个常用Linux文件操作命令的详细信息
- **多种查询方式**: 支持分类浏览、关键词搜索、精确查找
- **交互式界面**: 提供友好的交互式命令行界面
- **多种输出格式**: 支持表格、列表、树形、JSON等多种显示格式
- **智能搜索**: 支持精确匹配、前缀匹配、模糊匹配等多种搜索策略
- **详细的命令信息**: 包括语法、选项、示例、安全提示等全面信息
- **彩色输出**: 支持彩色高亮显示，提升阅读体验
- **分页显示**: 自动分页处理大量结果

## 系统要求

- Python 3.6+
- Linux操作系统
- 终端支持（推荐支持彩色输出的终端）

## 安装和使用

### 1. 下载项目

```bash
# 如果您有git（推荐）
git clone <repository-url>
cd linux-file-commands

# 或者直接下载并解压项目文件
```

### 2. 验证安装

```bash
# 运行验证脚本检查项目完整性
./verify.sh
```

### 3. 运行工具

```bash
# 方式1: 直接运行启动脚本
./linux-file-commands.py

# 方式2: 使用Python解释器
python3 linux-file-commands.py

# 方式3: 直接运行主程序
python3 src/main.py
```

## 使用方法

### 命令行模式

```bash
# 显示所有命令
./linux-file-commands.py --list

# 按分类显示命令
./linux-file-commands.py --category "基础文件操作"

# 搜索命令
./linux-file-commands.py --search "文件"

# 显示命令详情
./linux-file-commands.py --detail ls

# 查看帮助
./linux-file-commands.py --help
```

#### 高级选项

```bash
# 指定输出格式
./linux-file-commands.py --list --format table    # 表格格式（默认）
./linux-file-commands.py --list --format list     # 列表格式
./linux-file-commands.py --list --format json     # JSON格式

# 排序选项
./linux-file-commands.py --list --sort name       # 按名称排序（默认）
./linux-file-commands.py --list --sort category   # 按分类排序
./linux-file-commands.py --list --sort usage      # 按使用频率排序

# 过滤选项
./linux-file-commands.py --list --difficulty 初级  # 按难度过滤
./linux-file-commands.py --list --frequency 高频   # 按使用频率过滤

# 禁用颜色输出
./linux-file-commands.py --list --no-color

# 设置分页大小
./linux-file-commands.py --list --page-size 10
```

### 交互模式

直接运行工具（不带参数）将启动交互模式：

```bash
./linux-file-commands.py
```

在交互模式中可以使用以下命令：

```
linux-cmd> help                    # 显示帮助信息
linux-cmd> list                    # 显示所有命令
linux-cmd> category                # 显示所有分类
linux-cmd> category 基础文件操作    # 显示指定分类的命令
linux-cmd> search file            # 搜索包含"file"的命令
linux-cmd> detail ls              # 显示ls命令的详细信息
linux-cmd> quit                   # 退出程序
```

## 项目结构

```
linux-file-commands/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序
│   ├── parser.py          # 命令解析器
│   ├── category.py        # 分类管理器
│   ├── search.py          # 搜索引擎
│   ├── detail.py          # 详情管理器
│   └── formatter.py       # 输出格式化器
├── data/                  # 数据文件目录
│   ├── commands.json      # 命令数据库
│   └── categories.json    # 分类配置
├── tests/                 # 测试文件目录
│   └── test_all.py       # 测试套件
├── docs/                  # 文档目录
├── examples/              # 示例文件目录
├── linux-file-commands.py # 启动脚本
├── verify.sh             # 验证脚本
└── README.md             # 说明文档
```

## 支持的命令

### 基础文件操作
- **文件创建**: `touch`, `mkdir`
- **文件删除**: `rm`, `rmdir`
- **文件复制**: `cp`
- **文件移动**: `mv`

### 文件查看与编辑
- **内容查看**: `cat`, `less`, `head`, `tail`
- **内容处理**: `grep`

### 文件属性与权限
- **权限管理**: `chmod`, `chown`
- **属性查看**: `ls`
- **链接管理**: `ln`

### 文件查找与定位
- **文件查找**: `find`

### 压缩与归档
- **归档工具**: `tar`, `zip`, `unzip`

## 使用示例

### 示例1: 查找文件操作相关命令

```bash
$ ./linux-file-commands.py --search "文件"

=== 搜索结果: '文件' (8个匹配) ===

命令   | 描述                     | 相关度 | 匹配类型
-------|--------------------------|--------|----------
ls     | 列出目录内容             | 60%    | word_description  
cp     | 复制文件或目录           | 60%    | word_description
mv     | 移动/重命名文件或目录    | 60%    | word_description
rm     | 删除文件或目录           | 60%    | word_description
find   | 在目录树中搜索文件       | 60%    | word_description
```

### 示例2: 查看特定命令详情

```bash
$ ./linux-file-commands.py --detail ls

╔═══ ls ═══╗
列出目录内容
分类: 文件属性与权限, 基础文件操作

【语法】
  ls [选项] [文件...]
  [] 表示可选参数; ... 表示可以指定多个参数

【常用选项】
  -l       使用长格式列出信息
  -a       不隐藏任何以.开头的项目
  -h       与-l一起使用，以易读的格式列出文件大小
  -R       递归列出子目录

【使用示例】
  1. ls -la /home/user
     以长格式显示所有文件（包括隐藏文件）
  2. ls -lh *.txt
     以易读格式显示文件大小
  3. ls -R /var/log
     执行 ls 命令的示例用法

【相关命令】
  dir, tree, find

【安全提示】
  使用ls命令是安全的，不会修改任何文件

【附加信息】
  命令类型: 安全查看命令
  💡 这是基础命令，建议优先掌握
```

### 示例3: 按分类浏览命令

```bash
$ ./linux-file-commands.py --category "基础文件操作"

=== 基础文件操作 (6个命令) ===

• ls: 列出目录内容

• cp: 复制文件或目录

• mv: 移动/重命名文件或目录

• rm: 删除文件或目录

• mkdir: 创建目录

• touch: 创建空文件或更新文件时间戳
```

### 示例4: 交互模式使用

```bash
$ ./linux-file-commands.py

╔═══════════════════════════════════════════════════════════════╗
║                 Linux 文件操作命令查询工具                    ║
║                    版本 1.0.0                                ║
╚═══════════════════════════════════════════════════════════════╝

欢迎使用！输入 'help' 查看可用命令，输入 'quit' 退出。

linux-cmd> search copy
=== 搜索结果: 'copy' (1个匹配) ===

命令 | 描述           | 相关度 | 匹配类型
-----|----------------|--------|----------
cp   | 复制文件或目录 | 90%    | prefix_name

linux-cmd> detail cp
╔═══ cp ═══╗
复制文件或目录
分类: 基础文件操作, 文件复制
...

linux-cmd> quit
再见！
```

## 扩展和定制

### 添加新命令

要添加新命令，编辑 `data/commands.json` 文件：

```json
{
  "name": "新命令名",
  "categories": ["分类1", "分类2"],
  "description": "命令描述",
  "syntax": "命令语法",
  "common_options": [
    {
      "option": "-选项",
      "description": "选项描述"
    }
  ],
  "examples": [
    "使用示例1",
    "使用示例2"
  ],
  "related_commands": ["相关命令1", "相关命令2"],
  "safety_tips": "安全提示"
}
```

### 添加新分类

编辑 `data/categories.json` 文件来添加新的命令分类。

### 自定义输出格式

可以在 `src/formatter.py` 中自定义新的输出格式和样式。

## 故障排除

### 常见问题

1. **Python未找到**
   ```bash
   # 安装Python（Ubuntu/Debian）
   sudo apt update
   sudo apt install python3
   
   # 安装Python（CentOS/RHEL）
   sudo yum install python3
   ```

2. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x linux-file-commands.py
   chmod +x verify.sh
   ```

3. **字符编码问题**
   ```bash
   # 确保终端支持UTF-8编码
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

4. **颜色显示问题**
   ```bash
   # 如果颜色显示不正常，可以禁用颜色输出
   ./linux-file-commands.py --list --no-color
   ```

### 调试模式

要启用详细的错误信息，可以直接运行Python模块：

```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from main import main
main()
"
```

## 贡献指南

欢迎贡献代码和改进建议！

1. Fork本项目
2. 创建功能分支
3. 进行更改
4. 运行测试：`python3 tests/test_all.py`
5. 提交Pull Request

## 版本历史

- **v1.0.0** (2024): 初始版本
  - 实现基本的命令查询功能
  - 支持分类浏览和搜索
  - 提供交互式界面
  - 包含19个常用Linux文件操作命令

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。

## 联系信息

如有问题或建议，请通过以下方式联系：

- 创建Issue
- 发送Pull Request
- 邮件联系

---

**感谢使用Linux文件操作命令查询工具！希望它能帮助您更好地学习和使用Linux命令。**