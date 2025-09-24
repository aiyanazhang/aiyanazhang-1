"""
文件下载器实际应用场景演示
并发下载多个文件，展示实际的多线程应用
"""

import threading
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import concurrent.futures
import hashlib

# 可选的依赖导入
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests模块未安装，文件下载器将使用模拟模式")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    # tqdm的简单替代品
    class tqdm:
        def __init__(self, total=100, desc="", unit="%", position=0):
            self.total = total
            self.desc = desc
            self.n = 0
            self.disable = False
        
        def update(self, n):
            self.n += n
        
        def close(self):
            pass


class DownloadTask:
    """下载任务类"""
    
    def __init__(self, url: str, filename: Optional[str] = None, chunk_size: int = 8192):
        self.url = url
        self.filename = filename or self._generate_filename(url)
        self.chunk_size = chunk_size
        self.status = "pending"
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.speed: float = 0.0
        
    def _generate_filename(self, url: str) -> str:
        """从URL生成文件名"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = f"download_{hash(url) % 100000}.bin"
        return filename
    
    @property
    def progress(self) -> float:
        """下载进度百分比"""
        if self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100
    
    @property
    def duration(self) -> float:
        """下载耗时（秒）"""
        if not self.start_time:
            return 0.0
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'url': self.url,
            'filename': self.filename,
            'status': self.status,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
            'progress': self.progress,
            'duration': self.duration,
            'speed': self.speed,
            'error': self.error
        }


class FileDownloader:
    """文件下载器类"""
    
    def __init__(self, download_dir: str = "./downloads", max_workers: int = 4):
        self.download_dir = download_dir
        self.max_workers = max_workers
        self.tasks: List[DownloadTask] = []
        self.stats_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        print(f"📁 下载目录: {os.path.abspath(download_dir)}")
        print(f"🧵 最大并发数: {max_workers}")
    
    def add_download(self, url: str, filename: Optional[str] = None) -> DownloadTask:
        """添加下载任务"""
        task = DownloadTask(url, filename)
        self.tasks.append(task)
        return task
    
    def download_file(self, task: DownloadTask) -> Dict[str, Any]:
        """下载单个文件"""
        filepath = os.path.join(self.download_dir, task.filename)
        
        try:
            task.status = "downloading"
            task.start_time = datetime.now()
            
            print(f"[{threading.current_thread().name}] 开始下载: {task.url}")
            
            if not HAS_REQUESTS:
                # 模拟下载
                time.sleep(random.uniform(1, 3))  # 模拟下载时间
                task.total_bytes = random.randint(1000, 10000)
                task.downloaded_bytes = task.total_bytes
                
                # 创建模拟文件
                with open(filepath, 'wb') as f:
                    f.write(b"Mock downloaded data " * (task.total_bytes // 20))
                
                task.status = "completed"
                task.end_time = datetime.now()
                
                result_msg = f"✅ 模拟下载完成: {task.filename} ({task.downloaded_bytes:,} bytes, {task.duration:.2f}s)"
                print(f"[{threading.current_thread().name}] {result_msg}")
                
                return task.to_dict()
            
            # 真实下载逻辑
            # 发送HEAD请求获取文件大小
            try:
                head_response = requests.head(task.url, timeout=10)
                task.total_bytes = int(head_response.headers.get('content-length', 0))
            except:
                task.total_bytes = 0
            
            # 开始下载
            response = requests.get(task.url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 如果HEAD请求失败，从GET响应中获取文件大小
            if task.total_bytes == 0:
                task.total_bytes = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=task.chunk_size):
                    if chunk:
                        f.write(chunk)
                        task.downloaded_bytes += len(chunk)
                        
                        # 更新下载速度
                        if task.duration > 0:
                            task.speed = task.downloaded_bytes / task.duration
            
            task.status = "completed"
            task.end_time = datetime.now()
            
            # 验证文件
            actual_size = os.path.getsize(filepath)
            if task.total_bytes > 0 and actual_size != task.total_bytes:
                task.error = f"文件大小不匹配: 期望 {task.total_bytes}, 实际 {actual_size}"
                task.status = "error"
            
            result_msg = f"✅ 下载完成: {task.filename} ({task.downloaded_bytes:,} bytes, {task.duration:.2f}s)"
            print(f"[{threading.current_thread().name}] {result_msg}")
            
            return task.to_dict()
            
        except Exception as e:
            task.status = "error"
            task.error = f"下载错误: {str(e)}"
            task.end_time = datetime.now()
            print(f"[{threading.current_thread().name}] ❌ 下载失败: {task.filename} - {task.error}")
            return task.to_dict()
    
    def batch_download(self) -> List[Dict[str, Any]]:
        """批量下载文件"""
        if not self.tasks:
            print("❌ 没有下载任务")
            return []
        
        print(f"\n🚀 开始批量下载 {len(self.tasks)} 个文件")
        print("=" * 60)
        
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务
            future_to_task = {
                executor.submit(self.download_file, task): task 
                for task in self.tasks
            }
            
            # 监控下载进度
            completed = 0
            total = len(self.tasks)
            
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    progress = (completed / total) * 100
                    print(f"📊 总进度: {completed}/{total} ({progress:.1f}%)")
                    
                except Exception as e:
                    print(f"❌ 任务执行异常: {task.filename} - {e}")
                    results.append({
                        'url': task.url,
                        'filename': task.filename,
                        'status': 'error',
                        'error': str(e)
                    })
        
        end_time = time.time()
        
        # 统计结果
        self._print_download_summary(results, end_time - start_time)
        
        return results
    
    def download_with_progress(self) -> List[Dict[str, Any]]:
        """带进度条的下载"""
        if not self.tasks:
            print("❌ 没有下载任务")
            return []
        
        print(f"\n🚀 带进度条的批量下载 {len(self.tasks)} 个文件")
        print("=" * 60)
        
        results = []
        
        # 为每个任务创建进度条
        progress_bars = {}
        for task in self.tasks:
            progress_bars[task] = tqdm(
                total=100,
                desc=task.filename[:20],
                unit='%',
                position=len(progress_bars)
            )
        
        def download_with_progress_update(task: DownloadTask) -> Dict[str, Any]:
            """带进度更新的下载函数"""
            pbar = progress_bars[task]
            
            try:
                # 下载文件并更新进度
                result = self.download_file(task)
                pbar.update(100 - pbar.n)  # 完成剩余进度
                pbar.close()
                return result
                
            except Exception as e:
                pbar.close()
                raise e
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(download_with_progress_update, task)
                for task in self.tasks
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"\n❌ 下载异常: {e}")
        
        end_time = time.time()
        
        # 清理进度条
        for pbar in progress_bars.values():
            if not pbar.disable:
                pbar.close()
        
        print(f"\n" + "=" * 60)
        self._print_download_summary(results, end_time - start_time)
        
        return results
    
    def download_with_retry(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """带重试机制的下载"""
        print(f"\n🔄 带重试机制的下载 (最大重试: {max_retries})")
        print("=" * 60)
        
        results = []
        retry_tasks = self.tasks.copy()
        attempt = 1
        
        while retry_tasks and attempt <= max_retries + 1:
            print(f"\n🎯 第 {attempt} 次尝试 ({len(retry_tasks)} 个任务)")
            
            current_results = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self.download_file, task): task 
                    for task in retry_tasks
                }
                
                for future in concurrent.futures.as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        current_results.append(result)
                    except Exception as e:
                        current_results.append({
                            'url': task.url,
                            'filename': task.filename,
                            'status': 'error',
                            'error': str(e)
                        })
            
            # 分析结果，确定需要重试的任务
            successful = [r for r in current_results if r['status'] == 'completed']
            failed = [r for r in current_results if r['status'] == 'error']
            
            results.extend(successful)
            
            if attempt <= max_retries and failed:
                # 准备重试失败的任务
                retry_tasks = []
                for failed_result in failed:
                    for task in self.tasks:
                        if task.url == failed_result['url']:
                            # 重置任务状态
                            task.status = "pending"
                            task.downloaded_bytes = 0
                            task.start_time = None
                            task.end_time = None
                            task.error = None
                            retry_tasks.append(task)
                            break
                
                print(f"⚠️  {len(failed)} 个任务失败，准备重试...")
                time.sleep(1)  # 重试前等待
            else:
                results.extend(failed)
                break
            
            attempt += 1
        
        # 最终统计
        total_time = sum(r.get('duration', 0) for r in results if r.get('duration'))
        self._print_download_summary(results, total_time, max_retries)
        
        return results
    
    def _print_download_summary(self, results: List[Dict[str, Any]], total_time: float, max_retries: int = 0):
        """打印下载统计摘要"""
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'error']
        
        total_bytes = sum(r.get('downloaded_bytes', 0) for r in successful)
        avg_speed = total_bytes / total_time if total_time > 0 else 0
        
        print(f"\n📊 下载统计摘要:")
        print(f"  总文件数: {len(results)}")
        print(f"  成功下载: {len(successful)}")
        print(f"  下载失败: {len(failed)}")
        print(f"  成功率: {(len(successful) / len(results)) * 100:.1f}%")
        print(f"  总下载量: {total_bytes:,} bytes ({total_bytes / 1024 / 1024:.2f} MB)")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  平均速度: {avg_speed / 1024:.2f} KB/s")
        
        if max_retries > 0:
            print(f"  最大重试次数: {max_retries}")
        
        if failed:
            print(f"\n❌ 失败的下载:")
            for result in failed[:5]:  # 只显示前5个失败的
                print(f"    {result['filename']}: {result.get('error', '未知错误')}")
            if len(failed) > 5:
                print(f"    ... 还有 {len(failed) - 5} 个失败的下载")


def demo_file_downloader():
    """文件下载器演示"""
    print("🚀 文件下载器实际应用演示")
    print("=" * 60)
    
    # 创建下载器
    downloader = FileDownloader(download_dir="./downloads", max_workers=3)
    
    # 添加一些示例下载任务（使用公共的测试文件）
    test_urls = [
        "https://httpbin.org/bytes/1024",  # 1KB测试文件
        "https://httpbin.org/bytes/2048",  # 2KB测试文件
        "https://httpbin.org/bytes/4096",  # 4KB测试文件
        "https://httpbin.org/bytes/8192",  # 8KB测试文件
    ]
    
    for i, url in enumerate(test_urls):
        filename = f"test_file_{i+1}.bin"
        downloader.add_download(url, filename)
    
    print(f"📋 添加了 {len(downloader.tasks)} 个下载任务")
    
    # 演示1: 基础批量下载
    print(f"\n{'='*50}")
    print("📦 演示1: 基础批量下载")
    print(f"{'='*50}")
    
    results1 = downloader.batch_download()
    
    # 演示2: 带重试机制的下载
    print(f"\n{'='*50}")
    print("🔄 演示2: 带重试机制的下载")
    print(f"{'='*50}")
    
    # 重置任务状态
    for task in downloader.tasks:
        task.status = "pending"
        task.downloaded_bytes = 0
        task.start_time = None
        task.end_time = None
        task.error = None
    
    results2 = downloader.download_with_retry(max_retries=2)
    
    print(f"\n{'='*60}")
    print("✅ 文件下载器演示完成")
    print(f"{'='*60}")


def main():
    """主函数"""
    demo_file_downloader()


if __name__ == "__main__":
    main()