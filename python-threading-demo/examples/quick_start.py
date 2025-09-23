#!/usr/bin/env python3
"""
快速入门示例
"""

import sys
import os
import threading
import time

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def simple_thread_example():
    """简单的线程示例"""
    print("=== 简单线程示例 ===")
    
    def worker(name, count):
        """工作函数"""
        for i in range(count):
            print(f"[{name}] 工作步骤 {i+1}")
            time.sleep(0.5)
        print(f"[{name}] 工作完成")
    
    # 创建线程
    thread1 = threading.Thread(target=worker, args=("线程1", 3))
    thread2 = threading.Thread(target=worker, args=("线程2", 3))
    
    # 启动线程
    thread1.start()
    thread2.start()
    
    # 等待线程完成
    thread1.join()
    thread2.join()
    
    print("所有线程完成\n")

def queue_example():
    """队列通信示例"""
    print("=== 队列通信示例 ===")
    
    import queue
    
    task_queue = queue.Queue()
    
    def producer():
        """生产者"""
        for i in range(5):
            task = f"任务{i+1}"
            task_queue.put(task)
            print(f"[生产者] 生产: {task}")
            time.sleep(0.3)
    
    def consumer():
        """消费者"""
        while True:
            try:
                task = task_queue.get(timeout=2)
                print(f"[消费者] 处理: {task}")
                time.sleep(0.5)
                task_queue.task_done()
            except queue.Empty:
                break
    
    # 创建线程
    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)
    
    # 启动线程
    producer_thread.start()
    consumer_thread.start()
    
    # 等待完成
    producer_thread.join()
    consumer_thread.join()
    
    print("队列通信示例完成\n")

def main():
    """主函数"""
    print("🚀 Python多线程快速入门示例")
    print("=" * 40)
    
    simple_thread_example()
    queue_example()
    
    print("✅ 快速入门示例完成！")
    print("🎯 运行 'python main.py' 体验完整演示系统")

if __name__ == "__main__":
    main()