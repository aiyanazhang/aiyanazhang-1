"""
线程同步演示模块
展示各种线程同步原语的使用，确保线程安全和数据一致性
"""

import threading
import time
import random
from datetime import datetime
from typing import List, Dict, Any
import queue


class ThreadSyncDemo:
    """线程同步机制演示类"""
    
    def __init__(self):
        self.shared_data = {'counter': 0, 'items': []}
        
    def lock_demo(self) -> None:
        """Lock锁演示"""
        print(f"\n{'='*50}")
        print("🔒 Lock锁机制演示")
        print(f"{'='*50}")
        
        # 不安全的计数器（无锁）
        unsafe_counter = {'value': 0}
        
        def unsafe_increment(name: str, iterations: int):
            """不安全的递增操作"""
            for i in range(iterations):
                temp = unsafe_counter['value']
                time.sleep(0.0001)  # 模拟处理时间
                unsafe_counter['value'] = temp + 1
                if i % 500 == 0:
                    print(f"[{name}] 不安全计数: {unsafe_counter['value']}")
        
        print("🚫 无锁操作测试:")
        threads = []
        for i in range(3):
            thread = threading.Thread(target=unsafe_increment, args=(f"UnsafeWorker-{i+1}", 1000))
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        print(f"无锁结果: {unsafe_counter['value']} (期望: 3000)")
        print(f"数据竞争导致丢失: {3000 - unsafe_counter['value']} 次递增")
        
        # 安全的计数器（有锁）
        safe_counter = {'value': 0}
        counter_lock = threading.Lock()
        
        def safe_increment(name: str, iterations: int):
            """安全的递增操作"""
            for i in range(iterations):
                with counter_lock:
                    temp = safe_counter['value']
                    time.sleep(0.0001)  # 模拟处理时间
                    safe_counter['value'] = temp + 1
                if i % 500 == 0:
                    print(f"[{name}] 安全计数: {safe_counter['value']}")
        
        print(f"\n✅ 有锁操作测试:")
        threads = []
        for i in range(3):
            thread = threading.Thread(target=safe_increment, args=(f"SafeWorker-{i+1}", 1000))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        print(f"有锁结果: {safe_counter['value']} (期望: 3000)")
        print(f"执行时间: {end_time - start_time:.2f}秒")
        print(f"数据完整性: {'✅ 完整' if safe_counter['value'] == 3000 else '❌ 有误'}")
    
    def rlock_demo(self) -> None:
        """RLock递归锁演示"""
        print(f"\n{'='*50}")
        print("🔄 RLock递归锁演示")
        print(f"{'='*50}")
        
        # 递归锁演示
        rlock = threading.RLock()
        call_stack = []
        
        def recursive_function(name: str, depth: int, max_depth: int):
            """递归函数，需要多次获取同一个锁"""
            with rlock:
                call_info = f"[{name}] 深度 {depth}/{max_depth}"
                call_stack.append(call_info)
                print(call_info + f" - 获取锁成功")
                
                if depth < max_depth:
                    time.sleep(0.1)  # 模拟处理
                    recursive_function(name, depth + 1, max_depth)
                
                print(f"[{name}] 深度 {depth} - 释放锁")
        
        # 创建多个线程同时执行递归函数
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=recursive_function,
                args=(f"RecursiveWorker-{i+1}", 1, 3)
            )
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        print(f"\n📊 递归锁执行结果:")
        print(f"  执行时间: {end_time - start_time:.2f}秒")
        print(f"  调用记录数: {len(call_stack)}")
        print(f"  最后几次调用:")
        for call in call_stack[-6:]:
            print(f"    {call}")
    
    def condition_demo(self) -> None:
        """Condition条件变量演示"""
        print(f"\n{'='*50}")
        print("⏳ Condition条件变量演示")
        print(f"{'='*50}")
        
        # 缓冲区和条件变量
        buffer = []
        buffer_size = 5
        condition = threading.Condition()
        
        def producer(name: str, count: int):
            """生产者"""
            for i in range(count):
                with condition:
                    # 等待缓冲区有空间
                    while len(buffer) >= buffer_size:
                        print(f"[{name}] 缓冲区满，等待...")
                        condition.wait()
                    
                    # 生产物品
                    item = f"{name}-Item-{i+1}"
                    buffer.append(item)
                    print(f"[{name}] 生产: {item} (缓冲区: {len(buffer)}/{buffer_size})")
                    
                    # 通知消费者
                    condition.notify_all()
                
                time.sleep(random.uniform(0.1, 0.3))
            
            print(f"[{name}] 生产完成")
        
        def consumer(name: str):
            """消费者"""
            consumed_count = 0
            while consumed_count < 15:  # 总共消费15个物品
                with condition:
                    # 等待缓冲区有物品
                    while len(buffer) == 0:
                        print(f"[{name}] 缓冲区空，等待...")
                        if not condition.wait(timeout=3):  # 3秒超时
                            print(f"[{name}] 等待超时，退出")
                            return
                    
                    # 消费物品
                    if buffer:
                        item = buffer.pop(0)
                        consumed_count += 1
                        print(f"[{name}] 消费: {item} (缓冲区: {len(buffer)}/{buffer_size})")
                        
                        # 通知生产者
                        condition.notify_all()
                
                # 模拟消费时间
                time.sleep(random.uniform(0.2, 0.5))
            
            print(f"[{name}] 消费完成，共消费 {consumed_count} 个物品")
        
        # 创建线程
        producer_thread = threading.Thread(target=producer, args=("Producer", 10))
        consumer_threads = [
            threading.Thread(target=consumer, args=(f"Consumer-{i+1}",))
            for i in range(2)
        ]
        
        start_time = time.time()
        
        # 启动线程
        producer_thread.start()
        for thread in consumer_threads:
            thread.start()
        
        # 等待完成
        producer_thread.join()
        for thread in consumer_threads:
            thread.join()
        
        end_time = time.time()
        
        print(f"\n📊 Condition演示结果:")
        print(f"  执行时间: {end_time - start_time:.2f}秒")
        print(f"  最终缓冲区: {buffer}")
        print(f"  剩余物品数: {len(buffer)}")
    
    def event_demo(self) -> None:
        """Event事件同步演示"""
        print(f"\n{'='*50}")
        print("📢 Event事件同步演示")
        print(f"{'='*50}")
        
        # 创建事件对象
        start_event = threading.Event()
        stop_event = threading.Event()
        
        # 工作结果收集
        results = []
        results_lock = threading.Lock()
        
        def worker(name: str, work_duration: float):
            """工作线程"""
            print(f"[{name}] 等待开始信号...")
            start_event.wait()  # 等待开始信号
            
            print(f"[{name}] 收到开始信号，开始工作...")
            
            # 模拟工作过程
            work_progress = 0
            step = 0.1
            while work_progress < work_duration and not stop_event.is_set():
                time.sleep(step)
                work_progress += step
                
                if int(work_progress * 10) % 10 == 0:  # 每秒报告进度
                    progress = (work_progress / work_duration) * 100
                    print(f"[{name}] 工作进度: {progress:.0f}%")
            
            if stop_event.is_set():
                print(f"[{name}] 收到停止信号，提前结束")
                status = "stopped"
            else:
                print(f"[{name}] 工作完成")
                status = "completed"
            
            # 记录结果
            with results_lock:
                results.append({
                    'worker': name,
                    'duration': work_progress,
                    'status': status,
                    'completion_time': datetime.now()
                })
        
        def coordinator():
            """协调器线程"""
            print("[Coordinator] 准备启动所有工作线程...")
            time.sleep(1)  # 确保所有worker都在等待
            
            print("[Coordinator] 发送开始信号！")
            start_event.set()  # 发送开始信号
            
            # 让工作线程运行一段时间
            time.sleep(3)
            
            print("[Coordinator] 发送停止信号！")
            stop_event.set()  # 发送停止信号
        
        # 创建工作线程
        workers = [
            threading.Thread(target=worker, args=(f"Worker-{i+1}", random.uniform(2, 5)))
            for i in range(4)
        ]
        
        coordinator_thread = threading.Thread(target=coordinator)
        
        # 启动所有线程
        start_time = time.time()
        
        for w in workers:
            w.start()
        
        coordinator_thread.start()
        
        # 等待完成
        coordinator_thread.join()
        for w in workers:
            w.join()
        
        end_time = time.time()
        
        # 分析结果
        print(f"\n📊 Event同步结果:")
        print(f"  总执行时间: {end_time - start_time:.2f}秒")
        print(f"  工作线程数: {len(workers)}")
        
        completed_count = sum(1 for r in results if r['status'] == 'completed')
        stopped_count = sum(1 for r in results if r['status'] == 'stopped')
        
        print(f"  完成工作: {completed_count} 个线程")
        print(f"  提前停止: {stopped_count} 个线程")
        
        print(f"\n📋 详细结果:")
        for result in results:
            print(f"  {result['worker']}: {result['status']} "
                  f"(工作时长: {result['duration']:.1f}秒)")
    
    def semaphore_demo(self) -> None:
        """Semaphore信号量演示"""
        print(f"\n{'='*50}")
        print("🚦 Semaphore信号量演示")
        print(f"{'='*50}")
        
        # 创建信号量（模拟资源池）
        resource_pool_size = 3
        semaphore = threading.Semaphore(resource_pool_size)
        
        # 资源使用统计
        resource_usage = {'current': 0, 'max_used': 0, 'total_requests': 0}
        usage_lock = threading.Lock()
        
        def use_resource(name: str, work_duration: float):
            """使用有限资源的工作函数"""
            with usage_lock:
                resource_usage['total_requests'] += 1
            
            print(f"[{name}] 请求资源...")
            
            # 获取资源
            semaphore.acquire()
            
            try:
                with usage_lock:
                    resource_usage['current'] += 1
                    if resource_usage['current'] > resource_usage['max_used']:
                        resource_usage['max_used'] = resource_usage['current']
                
                print(f"[{name}] 获得资源，开始工作... "
                      f"(当前使用: {resource_usage['current']}/{resource_pool_size})")
                
                # 模拟使用资源
                time.sleep(work_duration)
                
                print(f"[{name}] 工作完成，释放资源")
                
            finally:
                with usage_lock:
                    resource_usage['current'] -= 1
                semaphore.release()
        
        # 创建更多的工作线程（超过资源数量）
        workers = []
        for i in range(8):  # 8个线程竞争3个资源
            work_duration = random.uniform(1, 3)
            thread = threading.Thread(
                target=use_resource,
                args=(f"Worker-{i+1}", work_duration)
            )
            workers.append(thread)
        
        print(f"🚀 启动 {len(workers)} 个工作线程竞争 {resource_pool_size} 个资源")
        
        start_time = time.time()
        
        # 启动所有线程
        for worker in workers:
            worker.start()
        
        # 监控资源使用情况
        monitor_duration = 0
        while any(w.is_alive() for w in workers):
            time.sleep(0.5)
            monitor_duration += 0.5
            with usage_lock:
                current_usage = resource_usage['current']
            print(f"⏱️  监控 ({monitor_duration:.1f}s): 当前资源使用 {current_usage}/{resource_pool_size}")
        
        # 等待所有线程完成
        for worker in workers:
            worker.join()
        
        end_time = time.time()
        
        # 统计结果
        print(f"\n📊 Semaphore资源管理结果:")
        print(f"  总执行时间: {end_time - start_time:.2f}秒")
        print(f"  资源池大小: {resource_pool_size}")
        print(f"  总请求数: {resource_usage['total_requests']}")
        print(f"  最大并发使用: {resource_usage['max_used']}")
        print(f"  资源利用率: {(resource_usage['max_used'] / resource_pool_size) * 100:.1f}%")
        print(f"  平均等待时间: {((end_time - start_time) - sum(random.uniform(1, 3) for _ in range(8))) / 8:.2f}秒")
    
    def deadlock_demo(self) -> None:
        """死锁演示和避免"""
        print(f"\n{'='*50}")
        print("☠️  死锁演示和避免")
        print(f"{'='*50}")
        
        # 创建两个锁
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        
        def worker1():
            """工作线程1 - 可能导致死锁"""
            print("[Worker1] 尝试获取 Lock1...")
            with lock1:
                print("[Worker1] 获得 Lock1，工作中...")
                time.sleep(0.5)
                
                print("[Worker1] 尝试获取 Lock2...")
                try:
                    if lock2.acquire(timeout=2):  # 设置超时避免死锁
                        try:
                            print("[Worker1] 获得 Lock2，完成工作")
                            time.sleep(0.5)
                        finally:
                            lock2.release()
                            print("[Worker1] 释放 Lock2")
                    else:
                        print("[Worker1] ⚠️  获取 Lock2 超时，避免死锁")
                except:
                    print("[Worker1] ❌ 获取 Lock2 失败")
            
            print("[Worker1] 释放 Lock1，退出")
        
        def worker2():
            """工作线程2 - 可能导致死锁"""
            print("[Worker2] 尝试获取 Lock2...")
            with lock2:
                print("[Worker2] 获得 Lock2，工作中...")
                time.sleep(0.5)
                
                print("[Worker2] 尝试获取 Lock1...")
                try:
                    if lock1.acquire(timeout=2):  # 设置超时避免死锁
                        try:
                            print("[Worker2] 获得 Lock1，完成工作")
                            time.sleep(0.5)
                        finally:
                            lock1.release()
                            print("[Worker2] 释放 Lock1")
                    else:
                        print("[Worker2] ⚠️  获取 Lock1 超时，避免死锁")
                except:
                    print("[Worker2] ❌ 获取 Lock1 失败")
            
            print("[Worker2] 释放 Lock2，退出")
        
        print("🔄 启动可能死锁的线程（已添加超时保护）...")
        
        thread1 = threading.Thread(target=worker1)
        thread2 = threading.Thread(target=worker2)
        
        start_time = time.time()
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        end_time = time.time()
        
        print(f"\n✅ 死锁避免演示完成，耗时: {end_time - start_time:.2f}秒")
        print("💡 避免死锁的方法:")
        print("   1. 设置锁获取超时")
        print("   2. 按固定顺序获取多个锁")
        print("   3. 使用上下文管理器确保锁释放")
        print("   4. 减少锁的持有时间")
    
    def run_all_demos(self) -> None:
        """运行所有线程同步演示"""
        print("🚀 开始线程同步演示")
        print("=" * 60)
        
        try:
            self.lock_demo()
            self.rlock_demo()
            self.condition_demo()
            self.event_demo()
            self.semaphore_demo()
            self.deadlock_demo()
            
            print(f"\n{'='*60}")
            print("✅ 线程同步演示完成")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")


def main():
    """主函数"""
    demo = ThreadSyncDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()