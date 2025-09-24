"""
生产者消费者模式演示模块
实现经典的生产者消费者模式，展示线程间通信和数据交换机制
"""

import threading
import queue
import time
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class Task:
    """任务类"""
    
    def __init__(self, task_id: str, data: Any, priority: TaskPriority = TaskPriority.NORMAL):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None
    
    def __lt__(self, other):
        """支持优先级队列比较"""
        return self.priority.value > other.priority.value  # 数值越大优先级越高
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'task_id': self.task_id,
            'data': self.data,
            'priority': self.priority.name,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error
        }


class ProducerConsumerDemo:
    """生产者消费者模式演示类"""
    
    def __init__(self):
        self.stats = {
            'produced': 0,
            'consumed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        self.stats_lock = threading.Lock()
    
    def simple_producer_consumer(self) -> None:
        """简单生产者消费者演示"""
        print(f"\n{'='*50}")
        print("🏭 简单生产者消费者演示")
        print(f"{'='*50}")
        
        # 创建队列
        task_queue = queue.Queue(maxsize=10)
        results = []
        results_lock = threading.Lock()
        
        def producer(name: str, count: int):
            """生产者函数"""
            print(f"[{name}] 开始生产...")
            for i in range(count):
                item = f"{name}-Item-{i+1}"
                task_queue.put(item)
                print(f"[{name}] 生产: {item} (队列大小: {task_queue.qsize()})")
                time.sleep(random.uniform(0.1, 0.5))
            print(f"[{name}] 生产完成")
        
        def consumer(name: str):
            """消费者函数"""
            print(f"[{name}] 开始消费...")
            while True:
                try:
                    # 获取任务，超时5秒
                    item = task_queue.get(timeout=5)
                    
                    # 模拟处理时间
                    processing_time = random.uniform(0.2, 0.8)
                    time.sleep(processing_time)
                    
                    # 保存结果
                    result = {
                        'consumer': name,
                        'item': item,
                        'processing_time': processing_time,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    with results_lock:
                        results.append(result)
                    
                    print(f"[{name}] 消费: {item} (耗时: {processing_time:.2f}秒)")
                    
                    # 标记任务完成
                    task_queue.task_done()
                    
                except queue.Empty:
                    print(f"[{name}] 队列为空，消费者退出")
                    break
        
        # 创建线程
        producers = [
            threading.Thread(target=producer, args=("Producer-1", 5)),
            threading.Thread(target=producer, args=("Producer-2", 5))
        ]
        
        consumers = [
            threading.Thread(target=consumer, args=("Consumer-1",)),
            threading.Thread(target=consumer, args=("Consumer-2",)),
            threading.Thread(target=consumer, args=("Consumer-3",))
        ]
        
        # 启动所有线程
        start_time = time.time()
        
        for p in producers:
            p.start()
        
        for c in consumers:
            c.start()
        
        # 等待所有生产者完成
        for p in producers:
            p.join()
        
        print("\n📦 所有生产者完成，等待消费者处理完所有任务...")
        
        # 等待所有任务被消费
        task_queue.join()
        
        # 等待消费者线程结束
        for c in consumers:
            c.join()
        
        end_time = time.time()
        
        # 统计结果
        print(f"\n📊 执行统计:")
        print(f"  总耗时: {end_time - start_time:.2f}秒")
        print(f"  生产物品数: {len(results)}")
        print(f"  消费者数量: {len(consumers)}")
        
        # 按消费者分组统计
        consumer_stats = {}
        for result in results:
            consumer = result['consumer']
            if consumer not in consumer_stats:
                consumer_stats[consumer] = {'count': 0, 'total_time': 0}
            consumer_stats[consumer]['count'] += 1
            consumer_stats[consumer]['total_time'] += result['processing_time']
        
        print(f"\n📈 消费者统计:")
        for consumer, stats in consumer_stats.items():
            avg_time = stats['total_time'] / stats['count']
            print(f"  {consumer}: 处理 {stats['count']} 个任务, 平均耗时 {avg_time:.2f}秒")
    
    def priority_queue_demo(self) -> None:
        """优先级队列演示"""
        print(f"\n{'='*50}")
        print("⭐ 优先级队列演示")
        print(f"{'='*50}")
        
        # 创建优先级队列
        priority_queue = queue.PriorityQueue()
        completed_tasks = []
        completed_lock = threading.Lock()
        
        def priority_producer(name: str):
            """优先级生产者"""
            print(f"[{name}] 开始生产优先级任务...")
            
            # 生产不同优先级的任务
            tasks_to_produce = [
                ("urgent-task-1", TaskPriority.URGENT),
                ("normal-task-1", TaskPriority.NORMAL),
                ("high-task-1", TaskPriority.HIGH),
                ("low-task-1", TaskPriority.LOW),
                ("urgent-task-2", TaskPriority.URGENT),
                ("normal-task-2", TaskPriority.NORMAL),
                ("high-task-2", TaskPriority.HIGH),
                ("low-task-2", TaskPriority.LOW),
            ]
            
            for task_id, priority in tasks_to_produce:
                task = Task(task_id, f"Data for {task_id}", priority)
                priority_queue.put(task)
                print(f"[{name}] 生产: {task_id} (优先级: {priority.name})")
                time.sleep(0.2)
            
            print(f"[{name}] 生产完成")
        
        def priority_consumer(name: str):
            """优先级消费者"""
            print(f"[{name}] 开始消费优先级任务...")
            
            while True:
                try:
                    task = priority_queue.get(timeout=3)
                    task.started_at = datetime.now()
                    
                    print(f"[{name}] 开始处理: {task.task_id} (优先级: {task.priority.name})")
                    
                    # 模拟处理时间（高优先级任务处理更快）
                    if task.priority == TaskPriority.URGENT:
                        processing_time = random.uniform(0.1, 0.3)
                    elif task.priority == TaskPriority.HIGH:
                        processing_time = random.uniform(0.3, 0.6)
                    elif task.priority == TaskPriority.NORMAL:
                        processing_time = random.uniform(0.6, 1.0)
                    else:  # LOW
                        processing_time = random.uniform(1.0, 1.5)
                    
                    time.sleep(processing_time)
                    
                    task.completed_at = datetime.now()
                    task.result = f"Processed {task.data}"
                    
                    with completed_lock:
                        completed_tasks.append(task)
                    
                    print(f"[{name}] 完成: {task.task_id} (耗时: {processing_time:.2f}秒)")
                    priority_queue.task_done()
                    
                except queue.Empty:
                    print(f"[{name}] 队列为空，消费者退出")
                    break
        
        # 创建线程
        producer_thread = threading.Thread(target=priority_producer, args=("PriorityProducer",))
        consumer_threads = [
            threading.Thread(target=priority_consumer, args=(f"PriorityConsumer-{i+1}",))
            for i in range(2)
        ]
        
        # 启动线程
        start_time = time.time()
        
        producer_thread.start()
        for c in consumer_threads:
            c.start()
        
        # 等待完成
        producer_thread.join()
        priority_queue.join()
        
        for c in consumer_threads:
            c.join()
        
        end_time = time.time()
        
        # 分析结果
        print(f"\n📊 优先级队列执行分析:")
        print(f"  总耗时: {end_time - start_time:.2f}秒")
        print(f"  完成任务数: {len(completed_tasks)}")
        
        # 按优先级分组
        priority_groups = {}
        for task in completed_tasks:
            priority = task.priority.name
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(task)
        
        print(f"\n📈 按优先级统计:")
        for priority in ['URGENT', 'HIGH', 'NORMAL', 'LOW']:
            if priority in priority_groups:
                tasks = priority_groups[priority]
                count = len(tasks)
                avg_wait_time = sum(
                    (task.started_at - task.created_at).total_seconds() 
                    for task in tasks
                ) / count
                avg_processing_time = sum(
                    (task.completed_at - task.started_at).total_seconds() 
                    for task in tasks
                ) / count
                
                print(f"  {priority:>7}: {count} 个任务, "
                      f"平均等待 {avg_wait_time:.2f}秒, "
                      f"平均处理 {avg_processing_time:.2f}秒")
        
        # 验证优先级顺序
        print(f"\n🔍 任务处理顺序验证:")
        for i, task in enumerate(completed_tasks[:8]):  # 显示前8个任务
            print(f"  {i+1}. {task.task_id} (优先级: {task.priority.name})")
    
    def multi_producer_consumer(self) -> None:
        """多生产者多消费者演示"""
        print(f"\n{'='*50}")
        print("🔄 多生产者多消费者演示")
        print(f"{'='*50}")
        
        # 创建队列和同步对象
        task_queue = queue.Queue(maxsize=20)
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        # 统计数据
        producer_stats = {}
        consumer_stats = {}
        stats_lock = threading.Lock()
        
        def producer(producer_id: int, task_count: int):
            """生产者函数"""
            name = f"Producer-{producer_id}"
            print(f"[{name}] 启动，计划生产 {task_count} 个任务")
            
            produced = 0
            for i in range(task_count):
                if stop_event.is_set():
                    break
                
                task_data = {
                    'producer_id': producer_id,
                    'task_number': i + 1,
                    'data': f"Task data from {name}",
                    'created_at': time.time()
                }
                
                try:
                    task_queue.put(task_data, timeout=2)
                    produced += 1
                    print(f"[{name}] 生产任务 {i+1} (队列: {task_queue.qsize()})")
                    time.sleep(random.uniform(0.1, 0.3))
                except queue.Full:
                    print(f"[{name}] 队列满，跳过任务 {i+1}")
            
            with stats_lock:
                producer_stats[producer_id] = produced
            
            print(f"[{name}] 完成，共生产 {produced} 个任务")
        
        def consumer(consumer_id: int):
            """消费者函数"""
            name = f"Consumer-{consumer_id}"
            print(f"[{name}] 启动")
            
            consumed = 0
            total_processing_time = 0
            
            while not stop_event.is_set():
                try:
                    task_data = task_queue.get(timeout=1)
                    start_time = time.time()
                    
                    # 模拟处理
                    processing_time = random.uniform(0.2, 0.8)
                    time.sleep(processing_time)
                    
                    # 计算等待时间
                    wait_time = start_time - task_data['created_at']
                    
                    result = {
                        'consumer_id': consumer_id,
                        'producer_id': task_data['producer_id'],
                        'task_number': task_data['task_number'],
                        'wait_time': wait_time,
                        'processing_time': processing_time,
                        'completed_at': time.time()
                    }
                    
                    results_queue.put(result)
                    consumed += 1
                    total_processing_time += processing_time
                    
                    print(f"[{name}] 处理任务 P{task_data['producer_id']}-T{task_data['task_number']} "
                          f"(等待: {wait_time:.2f}s, 处理: {processing_time:.2f}s)")
                    
                    task_queue.task_done()
                    
                except queue.Empty:
                    continue
            
            with stats_lock:
                consumer_stats[consumer_id] = {
                    'consumed': consumed,
                    'total_processing_time': total_processing_time,
                    'avg_processing_time': total_processing_time / consumed if consumed > 0 else 0
                }
            
            print(f"[{name}] 停止，共处理 {consumed} 个任务")
        
        # 创建多个生产者和消费者
        producers = [
            threading.Thread(target=producer, args=(i+1, 8))
            for i in range(3)  # 3个生产者
        ]
        
        consumers = [
            threading.Thread(target=consumer, args=(i+1,))
            for i in range(4)  # 4个消费者
        ]
        
        # 启动所有线程
        start_time = time.time()
        
        for p in producers:
            p.start()
        
        for c in consumers:
            c.start()
        
        # 等待所有生产者完成
        for p in producers:
            p.join()
        
        print("\n⏳ 等待所有任务被处理...")
        
        # 等待队列清空
        task_queue.join()
        
        # 停止消费者
        stop_event.set()
        
        for c in consumers:
            c.join(timeout=2)
        
        end_time = time.time()
        
        # 收集所有结果
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # 统计分析
        print(f"\n📊 多生产者多消费者统计:")
        print(f"  总执行时间: {end_time - start_time:.2f}秒")
        print(f"  完成任务总数: {len(results)}")
        
        print(f"\n🏭 生产者统计:")
        total_produced = 0
        for producer_id, produced in producer_stats.items():
            print(f"  Producer-{producer_id}: 生产 {produced} 个任务")
            total_produced += produced
        print(f"  总生产: {total_produced} 个任务")
        
        print(f"\n🔄 消费者统计:")
        total_consumed = 0
        for consumer_id, stats in consumer_stats.items():
            print(f"  Consumer-{consumer_id}: 处理 {stats['consumed']} 个任务, "
                  f"平均处理时间 {stats['avg_processing_time']:.2f}秒")
            total_consumed += stats['consumed']
        print(f"  总消费: {total_consumed} 个任务")
        
        # 性能分析
        if results:
            avg_wait_time = sum(r['wait_time'] for r in results) / len(results)
            avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
            throughput = len(results) / (end_time - start_time)
            
            print(f"\n📈 性能指标:")
            print(f"  平均等待时间: {avg_wait_time:.2f}秒")
            print(f"  平均处理时间: {avg_processing_time:.2f}秒")
            print(f"  吞吐量: {throughput:.2f} 任务/秒")
            print(f"  队列利用率: {(total_produced - total_consumed) / 20 * 100:.1f}%")
    
    def run_all_demos(self) -> None:
        """运行所有生产者消费者演示"""
        print("🚀 开始生产者消费者演示")
        print("=" * 60)
        
        try:
            self.simple_producer_consumer()
            self.priority_queue_demo()
            self.multi_producer_consumer()
            
            print(f"\n{'='*60}")
            print("✅ 生产者消费者演示完成")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")


def main():
    """主函数"""
    demo = ProducerConsumerDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()