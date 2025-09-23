"""
信号量演示模块

演示Semaphore控制资源访问
"""

import threading
import time
import random
from typing import List, Dict, Any


class SemaphoreDemo:
    """信号量演示"""
    
    def demo_basic_semaphore(self):
        """演示基础信号量使用"""
        print("\n=== 基础信号量演示 ===")
        print("演示信号量限制并发访问数量")
        
        # 创建信号量，允许最多3个线程同时访问
        semaphore = threading.Semaphore(3)
        results = []
        
        def limited_resource_access(worker_id: int):
            """受限资源访问"""
            print(f"[Worker{worker_id}] 等待访问资源...")
            
            with semaphore:  # 使用信号量保护
                print(f"[Worker{worker_id}] 获得资源访问权限")
                # 模拟资源使用
                work_time = random.uniform(2, 4)
                time.sleep(work_time)
                results.append(f"Worker{worker_id} 完成工作，用时 {work_time:.1f}秒")
                print(f"[Worker{worker_id}] 释放资源")
                
        # 创建多个工作线程
        threads = []
        for i in range(6):  # 6个线程竞争3个资源
            thread = threading.Thread(
                target=limited_resource_access,
                args=(i+1,),
                name=f"Worker{i+1}"
            )
            threads.append(thread)
            
        print("创建6个工作线程竞争3个资源访问权限")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print("\n工作结果:")
        for result in results:
            print(f"  - {result}")
            
    def demo_database_connection_pool(self):
        """演示数据库连接池"""
        print("\n=== 数据库连接池演示 ===")
        
        class DatabaseConnectionPool:
            """模拟数据库连接池"""
            
            def __init__(self, max_connections: int = 3):
                self.max_connections = max_connections
                self.semaphore = threading.Semaphore(max_connections)
                self.connections = [f"Connection{i+1}" for i in range(max_connections)]
                self.available = self.connections.copy()
                self.used = {}
                self.lock = threading.Lock()
                
            def get_connection(self) -> str:
                """获取数据库连接"""
                print(f"[{threading.current_thread().name}] 请求数据库连接...")
                
                self.semaphore.acquire()  # 获取连接许可
                
                with self.lock:
                    connection = self.available.pop()
                    self.used[connection] = threading.current_thread().name
                    print(f"[{threading.current_thread().name}] 获得连接: {connection}")
                    return connection
                    
            def release_connection(self, connection: str):
                """释放数据库连接"""
                with self.lock:
                    if connection in self.used:
                        del self.used[connection]
                        self.available.append(connection)
                        print(f"[{threading.current_thread().name}] 释放连接: {connection}")
                        
                self.semaphore.release()  # 释放连接许可
                
            def get_status(self) -> Dict[str, Any]:
                """获取连接池状态"""
                with self.lock:
                    return {
                        'total': self.max_connections,
                        'available': len(self.available),
                        'used': len(self.used),
                        'used_by': self.used.copy()
                    }
                    
        pool = DatabaseConnectionPool(3)
        
        def database_worker(worker_id: int):
            """数据库工作线程"""
            try:
                # 获取连接
                connection = pool.get_connection()
                
                # 模拟数据库操作
                operation_time = random.uniform(2, 5)
                print(f"[Worker{worker_id}] 使用 {connection} 执行数据库操作...")
                time.sleep(operation_time)
                print(f"[Worker{worker_id}] 数据库操作完成")
                
                # 释放连接
                pool.release_connection(connection)
                
            except Exception as e:
                print(f"[Worker{worker_id}] 数据库操作失败: {e}")
                
        # 创建多个数据库工作线程
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=database_worker,
                args=(i+1,),
                name=f"DBWorker{i+1}"
            )
            threads.append(thread)
            
        print("创建5个数据库工作线程使用3个连接的连接池")
        print(f"初始连接池状态: {pool.get_status()}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            time.sleep(0.5)  # 错开启动时间
            
        # 定期检查连接池状态
        for i in range(8):
            time.sleep(1)
            status = pool.get_status()
            print(f"连接池状态 ({i+1}): 可用{status['available']}, 使用中{status['used']}")
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        print(f"最终连接池状态: {pool.get_status()}")
        
    def demo_semaphore_with_timeout(self):
        """演示信号量超时机制"""
        print("\n=== 信号量超时演示 ===")
        
        semaphore = threading.Semaphore(2)  # 只允许2个并发
        
        def worker_with_timeout(worker_id: int, timeout: float):
            """带超时的工作线程"""
            print(f"[Worker{worker_id}] 尝试获取资源（超时: {timeout}秒）...")
            
            if semaphore.acquire(timeout=timeout):
                try:
                    print(f"[Worker{worker_id}] 成功获取资源")
                    # 模拟长时间工作
                    time.sleep(random.uniform(3, 6))
                    print(f"[Worker{worker_id}] 工作完成")
                finally:
                    semaphore.release()
            else:
                print(f"[Worker{worker_id}] 获取资源超时")
                
        # 创建不同超时时间的工作线程
        timeouts = [1.0, 2.0, 8.0, 3.0, 10.0]
        threads = []
        
        for i, timeout in enumerate(timeouts):
            thread = threading.Thread(
                target=worker_with_timeout,
                args=(i+1, timeout),
                name=f"TimeoutWorker{i+1}"
            )
            threads.append(thread)
            
        print("创建5个不同超时时间的工作线程")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print("超时演示完成")
        
    def run_all_demos(self):
        """运行所有信号量演示"""
        try:
            self.demo_basic_semaphore()
            time.sleep(1)
            
            self.demo_database_connection_pool()
            time.sleep(1)
            
            self.demo_semaphore_with_timeout()
            
        except Exception as e:
            print(f"信号量演示出错: {e}")


def main():
    demo = SemaphoreDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()