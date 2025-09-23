"""
条件变量演示模块

演示Condition的使用场景
"""

import threading
import time
import random
import queue
from typing import List, Any


class ProducerConsumerBuffer:
    """生产者-消费者缓冲区"""
    
    def __init__(self, max_size: int = 5):
        self.buffer: List[Any] = []
        self.max_size = max_size
        self.condition = threading.Condition()
        self.total_produced = 0
        self.total_consumed = 0
        
    def produce(self, item: Any) -> bool:
        """生产者放入数据"""
        with self.condition:
            # 等待缓冲区有空间
            while len(self.buffer) >= self.max_size:
                print(f"[{threading.current_thread().name}] 缓冲区满，等待...")
                self.condition.wait()
                
            self.buffer.append(item)
            self.total_produced += 1
            print(f"[{threading.current_thread().name}] 生产: {item}, 缓冲区: {len(self.buffer)}/{self.max_size}")
            
            # 通知消费者
            self.condition.notify()
            return True
            
    def consume(self) -> Any:
        """消费者取出数据"""
        with self.condition:
            # 等待缓冲区有数据
            while len(self.buffer) == 0:
                print(f"[{threading.current_thread().name}] 缓冲区空，等待...")
                self.condition.wait()
                
            item = self.buffer.pop(0)
            self.total_consumed += 1
            print(f"[{threading.current_thread().name}] 消费: {item}, 缓冲区: {len(self.buffer)}/{self.max_size}")
            
            # 通知生产者
            self.condition.notify()
            return item


class TaskScheduler:
    """任务调度器 - 演示多条件等待"""
    
    def __init__(self):
        self.pending_tasks = []
        self.running_tasks = []
        self.completed_tasks = []
        self.condition = threading.Condition()
        self.max_concurrent = 3
        self.shutdown = False
        
    def add_task(self, task_id: str, task_func, *args):
        """添加任务"""
        with self.condition:
            task = {'id': task_id, 'func': task_func, 'args': args, 'status': 'pending'}
            self.pending_tasks.append(task)
            print(f"添加任务: {task_id}")
            self.condition.notify_all()
            
    def get_next_task(self):
        """获取下一个任务"""
        with self.condition:
            # 等待有可用任务且未达到并发限制
            while (not self.pending_tasks or len(self.running_tasks) >= self.max_concurrent) and not self.shutdown:
                self.condition.wait()
                
            if self.shutdown:
                return None
                
            task = self.pending_tasks.pop(0)
            task['status'] = 'running'
            self.running_tasks.append(task)
            print(f"[{threading.current_thread().name}] 获取任务: {task['id']}")
            return task
            
    def complete_task(self, task):
        """完成任务"""
        with self.condition:
            self.running_tasks.remove(task)
            task['status'] = 'completed'
            self.completed_tasks.append(task)
            print(f"[{threading.current_thread().name}] 完成任务: {task['id']}")
            self.condition.notify_all()
            
    def stop_scheduler(self):
        """停止调度器"""
        with self.condition:
            self.shutdown = True
            self.condition.notify_all()


class ConditionDemo:
    """条件变量演示"""
    
    def demo_producer_consumer(self):
        """演示生产者-消费者模式"""
        print("\n=== 生产者-消费者演示 ===")
        
        buffer = ProducerConsumerBuffer(max_size=3)
        
        def producer(name: str, count: int):
            """生产者函数"""
            for i in range(count):
                item = f"{name}-Item{i+1}"
                buffer.produce(item)
                time.sleep(random.uniform(0.5, 1.5))
                
        def consumer(name: str, count: int):
            """消费者函数"""
            for i in range(count):
                item = buffer.consume()
                # 模拟处理时间
                time.sleep(random.uniform(1.0, 2.0))
                
        # 创建生产者和消费者线程
        threads = []
        
        # 2个生产者
        for i in range(2):
            thread = threading.Thread(
                target=producer,
                args=(f"Producer{i+1}", 3),
                name=f"Producer{i+1}"
            )
            threads.append(thread)
            
        # 2个消费者
        for i in range(2):
            thread = threading.Thread(
                target=consumer,
                args=(f"Consumer{i+1}", 3),
                name=f"Consumer{i+1}"
            )
            threads.append(thread)
            
        # 启动所有线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"生产者-消费者演示完成")
        print(f"总生产: {buffer.total_produced}, 总消费: {buffer.total_consumed}")
        
    def demo_task_scheduler(self):
        """演示任务调度器"""
        print("\n=== 任务调度器演示 ===")
        
        scheduler = TaskScheduler()
        
        def sample_task(task_name: str, duration: float):
            """示例任务"""
            print(f"[{threading.current_thread().name}] 执行任务 {task_name}")
            time.sleep(duration)
            
        def worker():
            """工作线程"""
            while True:
                task = scheduler.get_next_task()
                if task is None:  # 关闭信号
                    break
                    
                try:
                    # 执行任务
                    task['func'](*task['args'])
                    scheduler.complete_task(task)
                except Exception as e:
                    print(f"任务执行失败: {e}")
                    
        # 创建工作线程
        workers = []
        for i in range(3):
            thread = threading.Thread(target=worker, name=f"Worker{i+1}")
            thread.start()
            workers.append(thread)
            
        # 添加任务
        for i in range(8):
            scheduler.add_task(
                f"Task{i+1}",
                sample_task,
                f"Task{i+1}",
                random.uniform(1.0, 3.0)
            )
            time.sleep(0.2)
            
        # 等待所有任务完成
        time.sleep(5)
        
        # 停止调度器
        scheduler.stop_scheduler()
        
        # 等待工作线程退出
        for worker in workers:
            worker.join()
            
        print("任务调度器演示完成")
        
    def run_all_demos(self):
        """运行所有条件变量演示"""
        try:
            self.demo_producer_consumer()
            time.sleep(1)
            self.demo_task_scheduler()
        except Exception as e:
            print(f"条件变量演示出错: {e}")


def main():
    demo = ConditionDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()