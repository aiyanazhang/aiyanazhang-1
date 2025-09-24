# Python多线程演示系统使用示例

本文档提供了Python多线程演示系统的详细使用示例。

## 📋 目录

1. [基础使用](#基础使用)
2. [高级配置](#高级配置)
3. [实际应用案例](#实际应用案例)
4. [性能优化](#性能优化)
5. [故障排除](#故障排除)

## 基础使用

### 启动演示系统

#### 交互模式
```bash
python main.py
```

系统将显示菜单，可以选择运行特定的演示：
```
📋 请选择要运行的演示:
------------------------------------------------------------
  1. 🧵 基础线程演示
     展示Python threading模块的基本使用方法

  2. ⚡ 线程池演示
     展示concurrent.futures模块的ThreadPoolExecutor使用

  3. 🏭 生产者消费者演示
     实现经典的生产者消费者模式，展示线程间通信

  4. 🔒 线程同步演示
     展示各种线程同步原语的使用，确保线程安全

  5. 📥 文件下载器
     并发下载多个文件的实际应用场景

  6. 📊 数据处理器
     大数据集并行处理的实际应用场景

  7. 📋 日志分析器
     日志数据并行分析处理

  0. 🚀 运行所有演示
  q. 🚪 退出系统
------------------------------------------------------------
```

#### 命令行模式
```bash
# 运行所有演示
python main.py all

# 运行指定演示（基础线程和线程池）
python main.py 1 2

# 运行单个演示
python main.py 3
```

### 运行测试

```bash
# 运行完整测试套件
python tests/test_suite.py

# 运行特定测试类
python -m unittest tests.test_suite.TestBasicThreadDemo

# 运行测试并显示详细输出
python tests/test_suite.py -v
```

## 高级配置

### 自定义配置文件

编辑 `config/settings.conf` 来调整系统行为：

```ini
[system]
# 系统默认配置
default_max_workers = 8      # 增加默认线程数
default_chunk_size = 2000    # 增加数据块大小
default_timeout = 60         # 增加超时时间

[thread_pool]
# 线程池配置
max_workers = 8              # 根据CPU核心数调整
queue_size = 200             # 增加队列大小
timeout_seconds = 60

[file_downloader]
# 文件下载器配置
download_dir = /tmp/downloads # 自定义下载目录
max_workers = 6              # 增加下载并发数
chunk_size = 16384           # 增加下载块大小
retry_attempts = 5           # 增加重试次数

[data_processor]
# 数据处理器配置
max_workers = 8              # 增加处理线程数
chunk_size = 5000            # 增加数据块大小
enable_monitoring = true     # 启用性能监控
```

### 环境变量配置

```bash
# 设置下载目录
export THREADING_DEMO_DOWNLOAD_DIR="/path/to/downloads"

# 设置最大工作线程数
export THREADING_DEMO_MAX_WORKERS=8

# 设置调试模式
export THREADING_DEMO_DEBUG=true
```

## 实际应用案例

### 案例1：批量文件下载

```python
from src.file_downloader import FileDownloader

# 创建下载器
downloader = FileDownloader(download_dir="./downloads", max_workers=4)

# 添加下载任务
urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.pdf",
    "https://example.com/file3.mp4"
]

for i, url in enumerate(urls):
    downloader.add_download(url, f"file_{i+1}")

# 执行下载
results = downloader.batch_download()

# 检查结果
successful = [r for r in results if r['status'] == 'completed']
print(f"成功下载 {len(successful)} 个文件")
```

### 案例2：大数据集处理

```python
from src.data_processor import DataProcessor, DataGenerator

# 生成测试数据
data = DataGenerator.generate_sales_data(100000)  # 10万条销售记录

# 创建处理器
processor = DataProcessor(max_workers=8, chunk_size=5000)

# 并行处理
result = processor.parallel_processing(data, processor.process_sales_analytics)

# 查看结果
summary = result['summary']
print(f"处理了 {summary['total_records']} 条记录")
print(f"总销售额: ¥{summary['total_amount']:,.2f}")
```

### 案例3：自定义生产者消费者

```python
import queue
import threading
import time

# 创建队列
task_queue = queue.Queue(maxsize=50)
result_queue = queue.Queue()

def custom_producer(name, count):
    """自定义生产者"""
    for i in range(count):
        task = f"{name}_task_{i}"
        task_queue.put(task)
        print(f"生产: {task}")
        time.sleep(0.1)

def custom_consumer(name):
    """自定义消费者"""
    while True:
        try:
            task = task_queue.get(timeout=5)
            # 模拟处理
            time.sleep(0.2)
            result = f"processed_{task}"
            result_queue.put(result)
            print(f"[{name}] 处理: {task} -> {result}")
            task_queue.task_done()
        except queue.Empty:
            break

# 创建并启动线程
producer_thread = threading.Thread(target=custom_producer, args=("Producer", 20))
consumer_threads = [
    threading.Thread(target=custom_consumer, args=(f"Consumer-{i}",))
    for i in range(3)
]

producer_thread.start()
for t in consumer_threads:
    t.start()

# 等待完成
producer_thread.join()
task_queue.join()

for t in consumer_threads:
    t.join(timeout=1)
```

### 案例4：线程安全的计数器

```python
import threading

class ThreadSafeCounter:
    """线程安全的计数器"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    def get_value(self):
        with self._lock:
            return self._value

# 使用示例
counter = ThreadSafeCounter()

def worker():
    for _ in range(1000):
        counter.increment()

threads = [threading.Thread(target=worker) for _ in range(10)]

for t in threads:
    t.start()

for t in threads:
    t.join()

print(f"最终计数: {counter.get_value()}")  # 应该是10000
```

## 性能优化

### 线程数量优化

```python
import os
import psutil

def get_optimal_thread_count(task_type="io"):
    """获取最优线程数"""
    cpu_count = os.cpu_count()
    
    if task_type == "cpu":
        # CPU密集型任务
        return cpu_count
    elif task_type == "io":
        # IO密集型任务
        return cpu_count * 2
    elif task_type == "mixed":
        # 混合型任务
        return int(cpu_count * 1.5)
    else:
        return cpu_count

# 使用示例
optimal_threads = get_optimal_thread_count("io")
print(f"推荐线程数: {optimal_threads}")
```

### 内存使用监控

```python
import psutil
import threading
import time

def monitor_memory_usage(duration=10):
    """监控内存使用"""
    process = psutil.Process()
    
    def monitor():
        start_time = time.time()
        while time.time() - start_time < duration:
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            print(f"内存使用: {memory_info.rss / 1024 / 1024:.1f} MB, "
                  f"CPU使用: {cpu_percent:.1f}%")
            time.sleep(1)
    
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    return monitor_thread

# 启动监控
monitor_thread = monitor_memory_usage(30)
# ... 运行你的多线程代码 ...
monitor_thread.join()
```

### 性能基准测试

```python
import time
import concurrent.futures

def benchmark_thread_pool():
    """基准测试线程池性能"""
    
    def cpu_task(n):
        return sum(i * i for i in range(n))
    
    tasks = [5000] * 20
    
    # 测试不同的线程数
    for workers in [1, 2, 4, 8]:
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(cpu_task, tasks))
        
        end_time = time.time()
        
        print(f"线程数 {workers}: {end_time - start_time:.2f}秒")

benchmark_thread_pool()
```

## 故障排除

### 常见问题诊断

#### 问题1：线程死锁
```python
import threading
import time

def detect_deadlock():
    """死锁检测"""
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def worker1():
        with lock1:
            print("Worker1 获得 lock1")
            time.sleep(0.1)
            print("Worker1 尝试获得 lock2")
            if lock2.acquire(timeout=2):
                try:
                    print("Worker1 获得 lock2")
                finally:
                    lock2.release()
            else:
                print("Worker1 获取 lock2 超时 - 可能死锁")
    
    def worker2():
        with lock2:
            print("Worker2 获得 lock2")
            time.sleep(0.1)
            print("Worker2 尝试获得 lock1")
            if lock1.acquire(timeout=2):
                try:
                    print("Worker2 获得 lock1")
                finally:
                    lock1.release()
            else:
                print("Worker2 获取 lock1 超时 - 可能死锁")
    
    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

detect_deadlock()
```

#### 问题2：内存泄漏检测
```python
import gc
import threading
import time

def detect_memory_leak():
    """内存泄漏检测"""
    
    def leaky_function():
        # 模拟内存泄漏
        data = []
        for i in range(10000):
            data.append(f"data_{i}" * 100)
        # 故意不清理data
    
    # 运行前的对象计数
    gc.collect()
    before_count = len(gc.get_objects())
    
    # 运行可能泄漏的代码
    threads = []
    for i in range(10):
        t = threading.Thread(target=leaky_function)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 运行后的对象计数
    gc.collect()
    after_count = len(gc.get_objects())
    
    print(f"对象数量变化: {before_count} -> {after_count}")
    print(f"新增对象: {after_count - before_count}")
    
    if after_count - before_count > 1000:
        print("⚠️ 可能存在内存泄漏")
    else:
        print("✅ 内存使用正常")

detect_memory_leak()
```

#### 问题3：线程异常处理
```python
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def exception_handler():
    """线程异常处理"""
    
    def risky_function():
        import random
        if random.random() < 0.5:
            raise Exception("随机异常")
        return "成功"
    
    def safe_worker(worker_id):
        try:
            result = risky_function()
            logger.info(f"Worker {worker_id}: {result}")
        except Exception as e:
            logger.error(f"Worker {worker_id} 异常: {e}")
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=safe_worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

exception_handler()
```

### 调试技巧

#### 线程状态监控
```python
import threading
import time

def monitor_threads():
    """监控线程状态"""
    
    def worker(worker_id, duration):
        print(f"Worker {worker_id} 开始")
        time.sleep(duration)
        print(f"Worker {worker_id} 完成")
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i, 2))
        threads.append(t)
        t.start()
    
    # 监控线程状态
    while any(t.is_alive() for t in threads):
        active_count = threading.active_count()
        alive_threads = [t.name for t in threads if t.is_alive()]
        print(f"活跃线程数: {active_count}, 存活线程: {alive_threads}")
        time.sleep(0.5)
    
    print("所有线程完成")

monitor_threads()
```

---

这些示例涵盖了从基础使用到高级配置的各种场景。根据你的具体需求，可以选择相应的示例进行参考和修改。