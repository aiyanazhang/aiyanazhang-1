"""
基础线程演示模块
展示Python threading模块的基本使用方法
"""

import threading
import time
import random
from datetime import datetime
from typing import List, Any, Callable, Dict


class BasicThreadDemo:
    """基础线程操作演示类"""
    
    def __init__(self):
        self.results = []
        self.results_lock = threading.Lock()
    
    def simple_thread(self) -> None:
        """简单线程创建和启动演示"""
        print(f"\n{'='*50}")
        print("🧵 基础线程创建演示")
        print(f"{'='*50}")
        
        def worker(thread_name: str, delay: float):
            """工作线程函数"""
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 线程 {thread_name} 开始工作")
            time.sleep(delay)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 线程 {thread_name} 完成工作")
        
        # 创建多个线程
        threads = []
        for i in range(3):
            thread_name = f"Worker-{i+1}"
            delay = random.uniform(1, 3)
            thread = threading.Thread(target=worker, args=(thread_name, delay))
            threads.append(thread)
        
        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
            print(f"✅ 启动线程: {thread.name}")
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        print(f"\n⏱️  所有线程完成，总耗时: {end_time - start_time:.2f}秒")
    
    def thread_with_params(self) -> None:
        """带参数的线程演示"""
        print(f"\n{'='*50}")
        print("📋 线程参数传递演示")
        print(f"{'='*50}")
        
        def calculate_sum(start: int, end: int, thread_id: str):
            """计算指定范围内数字的和"""
            print(f"[{thread_id}] 开始计算 {start} 到 {end} 的和")
            total = sum(range(start, end + 1))
            
            with self.results_lock:
                self.results.append({
                    'thread_id': thread_id,
                    'range': f"{start}-{end}",
                    'result': total,
                    'timestamp': datetime.now()
                })
            
            print(f"[{thread_id}] 计算完成: {total}")
        
        # 清空之前的结果
        self.results.clear()
        
        # 创建多个计算任务
        tasks = [
            (1, 1000, "Thread-A"),
            (1001, 2000, "Thread-B"),
            (2001, 3000, "Thread-C"),
            (3001, 4000, "Thread-D")
        ]
        
        threads = []
        for start, end, thread_id in tasks:
            thread = threading.Thread(
                target=calculate_sum, 
                args=(start, end, thread_id),
                name=thread_id
            )
            threads.append(thread)
        
        # 启动并等待所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # 显示结果
        print(f"\n📊 计算结果汇总:")
        total_sum = 0
        for result in self.results:
            print(f"  {result['thread_id']}: 范围{result['range']} = {result['result']:,}")
            total_sum += result['result']
        
        print(f"\n🎯 总和: {total_sum:,}")
        print(f"⏱️  执行时间: {end_time - start_time:.2f}秒")
    
    def thread_with_return(self) -> List[Dict[str, Any]]:
        """线程返回值处理演示"""
        print(f"\n{'='*50}")
        print("🔄 线程返回值处理演示")
        print(f"{'='*50}")
        
        def fetch_data(url_id: int, delay: float) -> Dict[str, Any]:
            """模拟数据获取"""
            print(f"[Fetcher-{url_id}] 开始获取数据...")
            time.sleep(delay)  # 模拟网络延迟
            
            # 模拟返回数据
            data = {
                'url_id': url_id,
                'data': f"Data from source {url_id}",
                'size': random.randint(100, 1000),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            print(f"[Fetcher-{url_id}] 数据获取完成")
            return data
        
        # 使用列表和锁来收集结果
        results = []
        results_lock = threading.Lock()
        
        def worker_wrapper(url_id: int, delay: float):
            """工作线程包装器"""
            try:
                result = fetch_data(url_id, delay)
                with results_lock:
                    results.append(result)
            except Exception as e:
                with results_lock:
                    results.append({
                        'url_id': url_id,
                        'error': str(e),
                        'status': 'error'
                    })
        
        # 创建多个数据获取任务
        tasks = [(i, random.uniform(0.5, 2.0)) for i in range(1, 6)]
        threads = []
        
        start_time = time.time()
        
        for url_id, delay in tasks:
            thread = threading.Thread(
                target=worker_wrapper,
                args=(url_id, delay),
                name=f"Fetcher-{url_id}"
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # 显示结果
        print(f"\n📊 数据获取结果:")
        successful_results = [r for r in results if r.get('status') == 'success']
        error_results = [r for r in results if r.get('status') == 'error']
        
        for result in successful_results:
            print(f"  ✅ URL-{result['url_id']}: {result['data']} (大小: {result['size']} bytes)")
        
        for result in error_results:
            print(f"  ❌ URL-{result['url_id']}: 错误 - {result['error']}")
        
        print(f"\n📈 统计信息:")
        print(f"  总任务数: {len(tasks)}")
        print(f"  成功: {len(successful_results)}")
        print(f"  失败: {len(error_results)}")
        print(f"  执行时间: {end_time - start_time:.2f}秒")
        
        return results
    
    def demonstrate_thread_lifecycle(self) -> None:
        """演示线程生命周期"""
        print(f"\n{'='*50}")
        print("🔄 线程生命周期演示")
        print(f"{'='*50}")
        
        def long_running_task(task_name: str, duration: int):
            """长时间运行的任务"""
            print(f"[{task_name}] 任务开始 - 状态: {threading.current_thread().is_alive()}")
            
            for i in range(duration):
                time.sleep(1)
                print(f"[{task_name}] 进度: {i+1}/{duration} - 线程ID: {threading.get_ident()}")
            
            print(f"[{task_name}] 任务完成")
        
        # 创建线程
        thread = threading.Thread(
            target=long_running_task,
            args=("LifecycleDemo", 3),
            name="LifecycleThread"
        )
        
        print(f"线程创建 - 存活状态: {thread.is_alive()}")
        print(f"线程名称: {thread.name}")
        print(f"是否守护线程: {thread.daemon}")
        
        # 启动线程
        thread.start()
        print(f"线程启动 - 存活状态: {thread.is_alive()}")
        
        # 主线程继续执行其他工作
        print("主线程执行其他工作...")
        time.sleep(1)
        print(f"检查线程状态 - 存活状态: {thread.is_alive()}")
        
        # 等待线程完成
        thread.join()
        print(f"线程完成 - 存活状态: {thread.is_alive()}")
    
    def run_all_demos(self) -> None:
        """运行所有基础线程演示"""
        print("🚀 开始基础线程演示")
        print("=" * 60)
        
        try:
            self.simple_thread()
            self.thread_with_params()
            self.thread_with_return()
            self.demonstrate_thread_lifecycle()
            
            print(f"\n{'='*60}")
            print("✅ 基础线程演示完成")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")


def main():
    """主函数"""
    demo = BasicThreadDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()