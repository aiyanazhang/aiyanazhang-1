"""
线程通信演示模块

演示使用Queue、Event等进行线程间通信
"""

import threading
import queue
import time
import random
from typing import Any, Dict, List


class QueueDemo:
    """队列通信演示"""
    
    def demo_basic_queue(self):
        """演示基础队列通信"""
        print("\n=== 基础队列通信演示 ===")
        
        task_queue = queue.Queue(maxsize=5)
        result_queue = queue.Queue()
        
        def producer(producer_id: int, task_count: int):
            """生产者"""
            for i in range(task_count):
                task = f"Task-{producer_id}-{i+1}"
                task_queue.put(task)
                print(f"[Producer{producer_id}] 生产任务: {task}")
                time.sleep(random.uniform(0.5, 1.5))
                
        def consumer(consumer_id: int):
            """消费者"""
            while True:
                try:
                    task = task_queue.get(timeout=3)
                    print(f"[Consumer{consumer_id}] 处理任务: {task}")
                    
                    # 模拟处理时间
                    processing_time = random.uniform(1, 3)
                    time.sleep(processing_time)
                    
                    result = f"{task} 完成 (用时: {processing_time:.1f}s)"
                    result_queue.put(result)
                    
                    task_queue.task_done()
                    
                except queue.Empty:
                    print(f"[Consumer{consumer_id}] 超时，退出")
                    break
                    
        # 创建生产者和消费者线程
        threads = []
        
        # 2个生产者
        for i in range(2):
            thread = threading.Thread(
                target=producer,
                args=(i+1, 3),
                name=f"Producer{i+1}"
            )
            threads.append(thread)
            
        # 3个消费者
        for i in range(3):
            thread = threading.Thread(
                target=consumer,
                args=(i+1,),
                name=f"Consumer{i+1}"
            )
            threads.append(thread)
            
        # 启动所有线程
        for thread in threads:
            thread.start()
            
        # 等待生产者完成
        for thread in threads[:2]:  # 只等待生产者
            thread.join()
            
        # 等待所有任务完成
        task_queue.join()
        
        # 收集结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
            
        print(f"\n处理结果 ({len(results)} 个):")
        for result in results:
            print(f"  - {result}")


class EventDemo:
    """事件通信演示"""
    
    def demo_basic_event(self):
        """演示基础事件通信"""
        print("\n=== 基础事件通信演示 ===")
        
        start_event = threading.Event()
        stop_event = threading.Event()
        
        def worker(worker_id: int):
            """工作线程"""
            print(f"[Worker{worker_id}] 等待启动信号...")
            start_event.wait()  # 等待启动事件
            
            print(f"[Worker{worker_id}] 开始工作")
            
            # 工作循环
            step = 0
            while not stop_event.is_set():
                step += 1
                print(f"[Worker{worker_id}] 工作步骤 {step}")
                
                # 检查停止事件（带超时）
                if stop_event.wait(timeout=1):
                    break
                    
            print(f"[Worker{worker_id}] 收到停止信号，结束工作")
            
        def controller():
            """控制线程"""
            print("[Controller] 准备启动工作线程...")
            time.sleep(2)
            
            print("[Controller] 发送启动信号")
            start_event.set()
            
            time.sleep(5)
            
            print("[Controller] 发送停止信号")
            stop_event.set()
            
        # 创建线程
        threads = []
        
        # 控制线程
        controller_thread = threading.Thread(target=controller, name="Controller")
        threads.append(controller_thread)
        
        # 工作线程
        for i in range(3):
            worker_thread = threading.Thread(
                target=worker,
                args=(i+1,),
                name=f"Worker{i+1}"
            )
            threads.append(worker_thread)
            
        # 启动所有线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print("事件通信演示完成")


class SharedDataDemo:
    """共享数据演示"""
    
    def demo_thread_local(self):
        """演示线程本地存储"""
        print("\n=== 线程本地存储演示 ===")
        
        # 创建线程本地存储
        thread_local_data = threading.local()
        
        def worker(worker_id: int):
            """工作线程"""
            # 为当前线程设置本地数据
            thread_local_data.worker_id = worker_id
            thread_local_data.counter = 0
            thread_local_data.start_time = time.time()
            
            print(f"[Worker{worker_id}] 初始化线程本地数据")
            
            # 模拟工作
            for i in range(5):
                thread_local_data.counter += 1
                print(f"[Worker{worker_id}] 本地计数器: {thread_local_data.counter}")
                time.sleep(random.uniform(0.3, 0.8))
                
            # 显示线程本地数据
            elapsed = time.time() - thread_local_data.start_time
            print(f"[Worker{worker_id}] 完成工作，总计数: {thread_local_data.counter}, "
                  f"用时: {elapsed:.1f}秒")
                  
        # 创建多个工作线程
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=worker,
                args=(i+1,),
                name=f"LocalWorker{i+1}"
            )
            threads.append(thread)
            
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print("线程本地存储演示完成")
        
    def demo_shared_counter(self):
        """演示共享计数器"""
        print("\n=== 共享计数器演示 ===")
        
        class SharedCounter:
            """线程安全的共享计数器"""
            
            def __init__(self):
                self.value = 0
                self.lock = threading.Lock()
                self.updates = []
                
            def increment(self, thread_name: str):
                """增加计数"""
                with self.lock:
                    old_value = self.value
                    self.value += 1
                    self.updates.append(f"{thread_name}: {old_value} -> {self.value}")
                    print(f"[{thread_name}] 计数器: {old_value} -> {self.value}")
                    
            def get_value(self):
                """获取当前值"""
                with self.lock:
                    return self.value
                    
            def get_updates(self):
                """获取更新历史"""
                with self.lock:
                    return self.updates.copy()
                    
        counter = SharedCounter()
        
        def increment_worker(worker_id: int, increments: int):
            """增量工作线程"""
            for i in range(increments):
                counter.increment(f"Worker{worker_id}")
                time.sleep(random.uniform(0.1, 0.5))
                
        # 创建多个工作线程
        threads = []
        for i in range(4):
            thread = threading.Thread(
                target=increment_worker,
                args=(i+1, 5),
                name=f"CounterWorker{i+1}"
            )
            threads.append(thread)
            
        print("创建4个线程，每个线程增加计数器5次")
        print(f"初始计数器值: {counter.get_value()}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"最终计数器值: {counter.get_value()}")
        print(f"总更新次数: {len(counter.get_updates())}")


class CommunicationDemo:
    """综合通信演示"""
    
    def run_all_demos(self):
        """运行所有通信演示"""
        try:
            queue_demo = QueueDemo()
            queue_demo.demo_basic_queue()
            time.sleep(1)
            
            event_demo = EventDemo()
            event_demo.demo_basic_event()
            time.sleep(1)
            
            shared_demo = SharedDataDemo()
            shared_demo.demo_thread_local()
            time.sleep(1)
            shared_demo.demo_shared_counter()
            
        except Exception as e:
            print(f"通信演示出错: {e}")


def main():
    demo = CommunicationDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()