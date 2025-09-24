# Linux文件操作命令查询工具 - 使用示例

本文档提供了详细的使用示例，帮助您快速上手和充分利用本工具的各种功能。

## 快速开始

### 基本使用流程

```bash
# 1. 验证安装
./verify.sh

# 2. 查看帮助
./linux-file-commands.py --help

# 3. 列出所有命令
./linux-file-commands.py --list

# 4. 启动交互模式
./linux-file-commands.py
```

## 命令行模式示例

### 1. 列出所有命令

```bash
$ ./linux-file-commands.py --list

命令     | 描述                           | 分类
---------|--------------------------------|-------------------------
cat      | 显示文件内容                   | 文件查看与编辑, 内容查看
chmod    | 修改文件权限                   | 文件属性与权限, 权限管理
chown    | 修改文件所有者                 | 文件属性与权限, 权限管理
cp       | 复制文件或目录                 | 基础文件操作, 文件复制
find     | 在目录树中搜索文件             | 文件查找与定位, 文件查找
grep     | 搜索文本模式                   | 文件查看与编辑, 内容处理
head     | 显示文件开头部分               | 文件查看与编辑, 内容查看
less     | 分页显示文件内容               | 文件查看与编辑, 内容查看
ln       | 创建文件链接                   | 文件属性与权限, 链接管理
ls       | 列出目录内容                   | 文件属性与权限, 基础文件操作
mkdir    | 创建目录                       | 基础文件操作, 文件创建
mv       | 移动/重命名文件或目录          | 基础文件操作, 文件移动
rm       | 删除文件或目录                 | 基础文件操作, 文件删除
rmdir    | 删除空目录                     | 基础文件操作, 文件删除
tail     | 显示文件结尾部分               | 文件查看与编辑, 内容查看
tar      | 归档和压缩文件                 | 压缩与归档, 归档工具
touch    | 创建空文件或更新文件时间戳     | 基础文件操作, 文件创建
unzip    | 提取zip压缩文件                | 压缩与归档, 归档工具
zip      | 创建zip压缩文件                | 压缩与归档, 归档工具

第 1 页，共 1 页 (总计 19 项)
```

### 2. 按分类查看命令

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

### 3. 搜索特定命令

```bash
$ ./linux-file-commands.py --search "复制"

=== 搜索结果: '复制' (1个匹配) ===

命令 | 描述           | 相关度 | 匹配类型
-----|----------------|--------|-------------
cp   | 复制文件或目录 | 60%    | word_description
```

```bash
$ ./linux-file-commands.py --search "file"

=== 搜索结果: 'file' (5个匹配) ===

命令   | 描述                     | 相关度 | 匹配类型
-------|--------------------------|--------|-------------
find   | 在目录树中搜索文件       | 60%    | word_description
rm     | 删除文件或目录           | 60%    | word_description
mv     | 移动/重命名文件或目录    | 60%    | word_description
cp     | 复制文件或目录           | 60%    | word_description
ln     | 创建文件链接             | 60%    | word_description
```

### 4. 查看命令详情

```bash
$ ./linux-file-commands.py --detail cp

╔═══ cp ═══╗
复制文件或目录
分类: 基础文件操作, 文件复制

【语法】
  cp [选项] 源文件 目标文件
  [] 表示可选参数

【常用选项】
  -r       递归复制目录
  -i       覆盖前询问
  -p       保留文件属性
  -v       显示详细信息

【使用示例】
  1. cp file1.txt file2.txt
     执行 cp 命令的示例用法
  2. cp -r /home/user/docs /backup/
     递归复制目录
  3. cp -i *.txt /tmp/
     复制时如果目标文件存在会询问是否覆盖

【相关命令】
  mv, rsync, scp

【安全提示】
  使用-i选项避免意外覆盖文件

【附加信息】
  学习建议: 这是基础命令，建议优先掌握
```

### 5. 使用高级选项

#### 不同输出格式

```bash
# 表格格式（默认）
$ ./linux-file-commands.py --list --format table

# 列表格式
$ ./linux-file-commands.py --list --format list

• ls: 列出目录内容

• cat: 显示文件内容

• less: 分页显示文件内容
```

```bash
# JSON格式
$ ./linux-file-commands.py --list --format json

[
  {
    "命令": "cat",
    "描述": "显示文件内容",
    "分类": "文件查看与编辑, 内容查看"
  },
  {
    "命令": "chmod",
    "描述": "修改文件权限", 
    "分类": "文件属性与权限, 权限管理"
  }
]
```

#### 排序选项

```bash
# 按名称排序（默认）
$ ./linux-file-commands.py --list --sort name

# 按分类排序
$ ./linux-file-commands.py --list --sort category

# 按使用频率排序
$ ./linux-file-commands.py --list --sort usage
```

#### 过滤选项

```bash
# 按难度过滤
$ ./linux-file-commands.py --list --difficulty 初级

命令    | 描述                           | 分类
--------|--------------------------------|-------------------------
ls      | 列出目录内容                   | 文件属性与权限, 基础文件操作
cat     | 显示文件内容                   | 文件查看与编辑, 内容查看
cp      | 复制文件或目录                 | 基础文件操作, 文件复制
mv      | 移动/重命名文件或目录          | 基础文件操作, 文件移动
rm      | 删除文件或目录                 | 基础文件操作, 文件删除
mkdir   | 创建目录                       | 基础文件操作, 文件创建
touch   | 创建空文件或更新文件时间戳     | 基础文件操作, 文件创建
```

```bash
# 按使用频率过滤
$ ./linux-file-commands.py --list --frequency 高频

命令 | 描述                  | 分类
-----|----------------------|-------------------------
ls   | 列出目录内容         | 文件属性与权限, 基础文件操作
cp   | 复制文件或目录       | 基础文件操作, 文件复制
mv   | 移动/重命名文件或目录| 基础文件操作, 文件移动
rm   | 删除文件或目录       | 基础文件操作, 文件删除
cat  | 显示文件内容         | 文件查看与编辑, 内容查看
grep | 搜索文本模式         | 文件查看与编辑, 内容处理
```

#### 分页显示

```bash
# 设置每页显示5个结果
$ ./linux-file-commands.py --list --page-size 5

命令    | 描述                           | 分类
--------|--------------------------------|-------------------------
cat     | 显示文件内容                   | 文件查看与编辑, 内容查看
chmod   | 修改文件权限                   | 文件属性与权限, 权限管理
chown   | 修改文件所有者                 | 文件属性与权限, 权限管理
cp      | 复制文件或目录                 | 基础文件操作, 文件复制
find    | 在目录树中搜索文件             | 文件查找与定位, 文件查找

第 1 页，共 4 页 (总计 19 项)
```

#### 禁用颜色输出

```bash
$ ./linux-file-commands.py --list --no-color
```

## 交互模式示例

### 启动交互模式

```bash
$ ./linux-file-commands.py

╔═══════════════════════════════════════════════════════════════╗
║                 Linux 文件操作命令查询工具                    ║
║                    版本 1.0.0                                ║
╚═══════════════════════════════════════════════════════════════╝

欢迎使用！输入 'help' 查看可用命令，输入 'quit' 退出。

linux-cmd> 
```

### 交互模式命令示例

#### 1. 查看帮助

```bash
linux-cmd> help

可用命令:
  help, h                    - 显示此帮助信息
  list, l                    - 显示所有命令
  category [分类名], cat, c   - 显示分类或指定分类的命令
  search <关键词>, s         - 搜索命令
  detail <命令名>, d         - 显示命令详情
  quit, q, exit             - 退出程序

示例:
  > list                    # 显示所有命令
  > category 基础文件操作    # 显示基础文件操作分类的命令
  > search file            # 搜索包含"file"的命令
  > detail ls              # 显示ls命令的详细信息
```

#### 2. 列出所有命令

```bash
linux-cmd> list

命令     | 描述                           | 分类
---------|--------------------------------|-------------------------
cat      | 显示文件内容                   | 文件查看与编辑, 内容查看
chmod    | 修改文件权限                   | 文件属性与权限, 权限管理
chown    | 修改文件所有者                 | 文件属性与权限, 权限管理
cp       | 复制文件或目录                 | 基础文件操作, 文件复制
...
```

#### 3. 查看所有分类

```bash
linux-cmd> category

=== 命令分类 ===

分类               | 描述                         | 命令数
-------------------|------------------------------|-------
基础文件操作       | 基本的文件和目录操作命令     | 6
文件查看与编辑     | 查看和编辑文件内容的命令     | 5
文件属性与权限     | 管理文件属性和权限的命令     | 3
文件查找与定位     | 查找文件和定位命令的工具     | 1
压缩与归档         | 文件压缩和归档管理命令       | 3
```

#### 4. 查看特定分类

```bash
linux-cmd> category 压缩与归档

=== 压缩与归档 (3个命令) ===

• tar: 归档和压缩文件

• zip: 创建zip压缩文件

• unzip: 提取zip压缩文件
```

#### 5. 搜索命令

```bash
linux-cmd> search 删除

=== 搜索结果: '删除' (2个匹配) ===

命令   | 描述           | 相关度 | 匹配类型
-------|----------------|--------|-------------
rm     | 删除文件或目录 | 60%    | word_description
rmdir  | 删除空目录     | 60%    | word_description
```

#### 6. 查看命令详情

```bash
linux-cmd> detail rm

╔═══ rm ═══╗
删除文件或目录
分类: 基础文件操作, 文件删除

【语法】
  rm [选项] 文件...
  [] 表示可选参数; ... 表示可以指定多个参数

【常用选项】
  -r       递归删除目录
  -f       强制删除，不询问
  -i       删除前询问
  -v       显示详细信息

【使用示例】
  1. rm file.txt
     执行 rm 命令的示例用法
  2. rm -rf /tmp/olddir
     递归删除目录
  3. rm -i *.tmp
     删除时如果目标文件存在会询问是否覆盖

【相关命令】
  rmdir, unlink

【安全提示】
  危险命令！使用rm -rf需要极其小心，建议先使用ls确认文件列表

【附加信息】
  命令类型: 危险命令
  ⚠ 此命令会删除文件，使用时请谨慎
  学习建议: 这是基础命令，建议优先掌握
```

#### 7. 退出程序

```bash
linux-cmd> quit
再见！
```

## 实际应用场景

### 场景1：学习Linux基础命令

作为Linux初学者，想要系统学习文件操作命令：

```bash
# 1. 首先查看按难度分类的初级命令
$ ./linux-file-commands.py --list --difficulty 初级

# 2. 逐个学习每个命令的详细用法
$ ./linux-file-commands.py --detail ls
$ ./linux-file-commands.py --detail cp
$ ./linux-file-commands.py --detail mv

# 3. 查看相关命令，建立知识联系
linux-cmd> detail cp
# 查看输出中的"相关命令"部分，然后学习相关命令
linux-cmd> detail mv
linux-cmd> detail rsync
```

### 场景2：快速查找特定功能的命令

需要找到执行特定任务的命令：

```bash
# 查找文件压缩相关的命令
$ ./linux-file-commands.py --search "压缩"

# 查找权限管理相关的命令  
$ ./linux-file-commands.py --category "文件属性与权限"

# 查找文件查看相关的命令
$ ./linux-file-commands.py --search "查看"
```

### 场景3：系统管理员快速参考

作为系统管理员，需要快速查阅命令语法：

```bash
# 快速查看tar命令的语法和选项
$ ./linux-file-commands.py --detail tar --format compact

# 查看所有高频使用的命令
$ ./linux-file-commands.py --list --frequency 高频

# 在脚本中使用JSON格式获取命令信息
$ ./linux-file-commands.py --search "find" --format json
```

### 场景4：教学和培训

用于Linux培训课程：

```bash
# 1. 展示课程大纲（所有分类）
linux-cmd> category

# 2. 逐个分类进行讲解
linux-cmd> category 基础文件操作

# 3. 详细讲解每个命令
linux-cmd> detail ls
linux-cmd> detail cp

# 4. 让学员搜索特定功能的命令
linux-cmd> search 文件
```

### 场景5：脚本编写辅助

编写shell脚本时查找合适的命令：

```bash
# 查找文件操作相关命令
$ ./linux-file-commands.py --search "文件" --format list

# 查看命令的具体语法和选项
$ ./linux-file-commands.py --detail find

# 查找文件压缩解压命令
$ ./linux-file-commands.py --category "压缩与归档"
```

## 高级使用技巧

### 1. 组合使用命令行选项

```bash
# 搜索初级难度的高频命令
$ ./linux-file-commands.py --list --difficulty 初级 --frequency 高频 --format list

# 按分类显示，禁用颜色，设置分页
$ ./linux-file-commands.py --category "基础文件操作" --no-color --page-size 3
```

### 2. 管道和重定向

```bash
# 将结果保存到文件
$ ./linux-file-commands.py --list --format json > commands.json

# 与其他命令组合使用
$ ./linux-file-commands.py --list --format list | grep "文件"

# 统计命令数量
$ ./linux-file-commands.py --list --format list | wc -l
```

### 3. 创建别名简化使用

```bash
# 在 ~/.bashrc 中添加别名
alias lfc='./linux-file-commands.py'
alias lfc-search='./linux-file-commands.py --search'
alias lfc-detail='./linux-file-commands.py --detail'

# 使用别名
$ lfc-search "删除"
$ lfc-detail rm
```

### 4. 集成到开发环境

```bash
# 在vim中使用
:!./linux-file-commands.py --detail find

# 在tmux中创建专用窗口
tmux new-window -n 'linux-help' './linux-file-commands.py'
```

## 常见问题解决

### 1. 搜索没有结果

```bash
# 尝试使用更通用的关键词
linux-cmd> search file
# 而不是
linux-cmd> search 文档

# 查看所有可用的命令
linux-cmd> list

# 查看所有分类
linux-cmd> category
```

### 2. 显示格式问题

```bash
# 如果终端不支持彩色显示
$ ./linux-file-commands.py --list --no-color

# 如果内容过宽
$ ./linux-file-commands.py --list --format list

# 调整分页大小
$ ./linux-file-commands.py --list --page-size 10
```

### 3. 找不到特定命令

```bash
# 使用模糊搜索
linux-cmd> search copy  # 可能找到 cp 命令

# 查看所有分类，确定命令应该在哪个分类下
linux-cmd> category

# 使用相关命令功能
linux-cmd> detail ls  # 查看相关命令部分
```

## 进阶应用

### 创建学习计划

```bash
# 1. 生成学习清单
$ ./linux-file-commands.py --list --difficulty 初级 --format list > beginner-commands.txt

# 2. 按分类组织学习
$ ./linux-file-commands.py --category "基础文件操作" --format list > basic-file-ops.txt

# 3. 创建命令卡片
for cmd in ls cp mv rm mkdir touch; do
    echo "=== $cmd ===" >> command-cards.txt
    ./linux-file-commands.py --detail $cmd >> command-cards.txt
    echo "" >> command-cards.txt
done
```

### 自动化脚本示例

```bash
#!/bin/bash
# daily-command.sh - 每日推荐一个命令学习

# 获取所有命令列表
commands=$(./linux-file-commands.py --list --format json | jq -r '.[].命令' | tr -d ' ')

# 随机选择一个命令
random_cmd=$(echo "$commands" | shuf -n 1)

echo "=== 今日推荐命令: $random_cmd ==="
./linux-file-commands.py --detail "$random_cmd"
```

### 集成到其他工具

```python
#!/usr/bin/env python3
# command-helper.py - 集成示例

import subprocess
import json

def get_command_info(command_name):
    """获取命令信息"""
    result = subprocess.run([
        './linux-file-commands.py', 
        '--detail', command_name, 
        '--format', 'json'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

# 使用示例
info = get_command_info('ls')
if info:
    print(f"命令: {info['name']}")
    print(f"描述: {info['description']}")
```

通过这些详细的使用示例，您应该能够充分利用Linux文件操作命令查询工具的各种功能，无论是日常学习、工作参考还是教学培训都能得心应手。