"""
线程类继承演示模块

演示如何通过继承Thread类创建自定义线程
"""

import threading
import time
import random
import queue
from typing import Any, Dict, List, Optional


class WorkerThread(threading.Thread):
    """基础工作线程类"""
    
    def __init__(self, name: str, task_data: Any):
        super().__init__(name=name)
        self.task_data = task_data
        self.result = None
        self.start_time = None
        self.end_time = None
        self.exception = None
        
    def run(self):
        """重写run方法定义线程执行逻辑"""
        self.start_time = time.time()
        
        try:
            print(f"[{self.name}] 开始执行任务...")
            self.result = self.execute_task(self.task_data)
            print(f"[{self.name}] 任务执行完成")
            
        except Exception as e:
            self.exception = e
            print(f"[{self.name}] 任务执行失败: {e}")
            
        finally:
            self.end_time = time.time()
            
    def execute_task(self, data: Any) -> Any:
        """子类需要重写的任务执行方法"""
        raise NotImplementedError("子类必须实现execute_task方法")
        
    def get_execution_time(self) -> Optional[float]:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class CalculatorThread(WorkerThread):
    """计算线程类"""
    
    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数学计算任务"""
        operation = data.get('operation', 'sum')
        numbers = data.get('numbers', [])
        
        print(f"[{self.name}] 执行 {operation} 运算，数据量: {len(numbers)}")
        
        if operation == 'sum':
            result = sum(numbers)
        elif operation == 'product':
            result = 1
            for num in numbers:
                result *= num
        elif operation == 'square_sum':
            result = sum(x * x for x in numbers)
        else:
            raise ValueError(f"不支持的运算类型: {operation}")
            
        # 模拟计算时间
        time.sleep(random.uniform(0.5, 2.0))
        
        return {
            'operation': operation,
            'input_count': len(numbers),
            'result': result
        }


class FileProcessorThread(WorkerThread):
    """文件处理线程类"""
    
    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟文件处理任务"""
        file_path = data.get('file_path', '')
        process_type = data.get('process_type', 'read')
        
        print(f"[{self.name}] 处理文件: {file_path}, 类型: {process_type}")
        
        # 模拟文件处理时间
        processing_time = random.uniform(1.0, 3.0)
        time.sleep(processing_time)
        
        if process_type == 'read':
            # 模拟读取文件
            lines_count = random.randint(100, 1000)
            return {
                'file_path': file_path,
                'process_type': process_type,
                'lines_read': lines_count,
                'processing_time': processing_time
            }
        elif process_type == 'write':
            # 模拟写入文件
            bytes_written = random.randint(1000, 10000)
            return {
                'file_path': file_path,
                'process_type': process_type,
                'bytes_written': bytes_written,
                'processing_time': processing_time
            }
        else:
            raise ValueError(f"不支持的处理类型: {process_type}")


class MonitorThread(threading.Thread):
    """监控线程类"""
    
    def __init__(self, name: str, threads_to_monitor: List[threading.Thread], 
                 interval: float = 1.0):
        super().__init__(name=name)
        self.threads_to_monitor = threads_to_monitor
        self.interval = interval
        self.monitoring = True
        self.daemon = True  # 设置为守护线程
        
    def run(self):
        """监控其他线程的运行状态"""
        print(f"[{self.name}] 开始监控 {len(self.threads_to_monitor)} 个线程")
        
        while self.monitoring:
            alive_count = sum(1 for t in self.threads_to_monitor if t.is_alive())
            print(f"[{self.name}] 监控报告: {alive_count}/{len(self.threads_to_monitor)} 个线程运行中")
            
            # 显示每个线程的状态
            for thread in self.threads_to_monitor:
                status = "运行中" if thread.is_alive() else "已完成"
                print(f"  - {thread.name}: {status}")
                
            if alive_count == 0:
                print(f"[{self.name}] 所有被监控线程已完成，停止监控")
                break
                
            time.sleep(self.interval)
            
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False


class ThreadInheritanceDemo:
    """线程继承演示类"""
    
    def __init__(self):
        self.threads: List[threading.Thread] = []
        
    def demo_calculator_threads(self) -> None:
        """演示计算线程"""
        print("\n=== 计算线程演示 ===")
        print("演示继承Thread类创建计算线程")
        
        # 准备计算任务数据
        tasks = [
            {
                'name': 'SumCalculator',
                'data': {
                    'operation': 'sum',
                    'numbers': list(range(1, 1001))
                }
            },
            {
                'name': 'ProductCalculator',
                'data': {
                    'operation': 'product',
                    'numbers': list(range(1, 11))
                }
            },
            {
                'name': 'SquareSumCalculator',
                'data': {
                    'operation': 'square_sum',
                    'numbers': list(range(1, 101))
                }
            }
        ]
        
        # 创建计算线程
        calc_threads = []
        for task in tasks:
            thread = CalculatorThread(task['name'], task['data'])
            calc_threads.append(thread)
            
        print(f"创建了 {len(calc_threads)} 个计算线程")
        
        # 启动线程
        print("\n启动计算线程...")
        for thread in calc_threads:
            thread.start()
            
        # 等待完成
        print("等待计算完成...")
        for thread in calc_threads:
            thread.join()
            
        # 显示结果
        print("\n计算结果:")
        for thread in calc_threads:
            if thread.exception:
                print(f"  - {thread.name}: 执行失败 - {thread.exception}")
            else:
                exec_time = thread.get_execution_time()
                result = thread.result
                print(f"  - {thread.name}:")
                print(f"    运算: {result['operation']}")
                print(f"    结果: {result['result']}")
                print(f"    执行时间: {exec_time:.2f}秒")
                
    def demo_file_processor_threads(self) -> None:
        """演示文件处理线程"""
        print("\n=== 文件处理线程演示 ===")
        print("演示继承Thread类创建文件处理线程")
        
        # 准备文件处理任务
        file_tasks = [
            {
                'name': 'FileReader1',
                'data': {
                    'file_path': '/path/to/data1.txt',
                    'process_type': 'read'
                }
            },
            {
                'name': 'FileReader2',
                'data': {
                    'file_path': '/path/to/data2.txt',
                    'process_type': 'read'
                }
            },
            {
                'name': 'FileWriter1',
                'data': {
                    'file_path': '/path/to/output1.txt',
                    'process_type': 'write'
                }
            }
        ]
        
        # 创建文件处理线程
        file_threads = []
        for task in file_tasks:
            thread = FileProcessorThread(task['name'], task['data'])
            file_threads.append(thread)
            
        print(f"创建了 {len(file_threads)} 个文件处理线程")
        
        # 启动线程
        print("\n启动文件处理线程...")
        for thread in file_threads:
            thread.start()
            
        # 等待完成
        for thread in file_threads:
            thread.join()
            
        # 显示结果
        print("\n文件处理结果:")
        for thread in file_threads:
            if thread.exception:
                print(f"  - {thread.name}: 处理失败 - {thread.exception}")
            else:
                result = thread.result
                exec_time = thread.get_execution_time()
                print(f"  - {thread.name}:")
                print(f"    文件: {result['file_path']}")
                print(f"    类型: {result['process_type']}")
                if result['process_type'] == 'read':
                    print(f"    读取行数: {result['lines_read']}")
                else:
                    print(f"    写入字节: {result['bytes_written']}")
                print(f"    执行时间: {exec_time:.2f}秒")
                
    def demo_monitor_thread(self) -> None:
        """演示监控线程"""
        print("\n=== 监控线程演示 ===")
        print("演示监控线程监视其他线程的运行状态")
        
        # 创建一些工作线程
        work_threads = []
        for i in range(3):
            task_data = {
                'operation': 'square_sum',
                'numbers': list(range(1, 501))
            }
            thread = CalculatorThread(f'Worker-{i+1}', task_data)
            work_threads.append(thread)
            
        # 创建监控线程
        monitor = MonitorThread('ThreadMonitor', work_threads, interval=0.5)
        
        print(f"创建了 {len(work_threads)} 个工作线程和1个监控线程")
        
        # 启动监控线程
        monitor.start()
        
        # 启动工作线程
        print("\n启动工作线程...")
        for thread in work_threads:
            thread.start()
            
        # 等待工作线程完成
        for thread in work_threads:
            thread.join()
            
        # 停止监控
        monitor.stop_monitoring()
        monitor.join(timeout=1)
        
        print("所有线程执行完毕")
        
    def run_all_demos(self) -> None:
        """运行所有线程继承演示"""
        print("开始线程继承演示...")
        
        try:
            self.demo_calculator_threads()
            time.sleep(1)
            
            self.demo_file_processor_threads()
            time.sleep(1)
            
            self.demo_monitor_thread()
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示过程中发生错误: {e}")
        finally:
            print("\n线程继承演示结束")


def main():
    """主函数，用于测试"""
    demo = ThreadInheritanceDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()