"""
Python多线程演示系统测试套件
"""

import unittest
import threading
import time
import queue
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.basic_thread_demo import BasicThreadDemo
from src.thread_pool_demo import ThreadPoolDemo
from src.producer_consumer_demo import ProducerConsumerDemo, Task, TaskPriority
from src.thread_sync_demo import ThreadSyncDemo
from src.file_downloader import FileDownloader, DownloadTask
from src.data_processor import DataProcessor, DataGenerator, DataChunk


class TestBasicThreadDemo(unittest.TestCase):
    """基础线程演示测试类"""
    
    def setUp(self):
        self.demo = BasicThreadDemo()
    
    def test_thread_with_params(self):
        """测试带参数的线程"""
        self.demo.thread_with_params()
        
        # 验证结果
        self.assertGreater(len(self.demo.results), 0)
        
        # 验证每个结果都有正确的字段
        for result in self.demo.results:
            self.assertIn('thread_id', result)
            self.assertIn('range', result)
            self.assertIn('result', result)
            self.assertIn('timestamp', result)
    
    def test_thread_with_return(self):
        """测试线程返回值处理"""
        results = self.demo.thread_with_return()
        
        # 验证返回结果
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # 验证结果结构
        for result in results:
            self.assertIn('url_id', result)
            self.assertIn('status', result)


class TestThreadPoolDemo(unittest.TestCase):
    """线程池演示测试类"""
    
    def setUp(self):
        self.demo = ThreadPoolDemo()
    
    def test_result_collection(self):
        """测试结果收集功能"""
        results = self.demo.result_collection()
        
        # 验证返回的是列表
        self.assertIsInstance(results, list)
        
        # 验证结果中包含成功和可能的失败项
        successful_results = [r for r in results if r.get('status') == 'success']
        self.assertGreater(len(successful_results), 0)


class TestProducerConsumerDemo(unittest.TestCase):
    """生产者消费者演示测试类"""
    
    def setUp(self):
        self.demo = ProducerConsumerDemo()
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task("test_task", {"data": "test"}, TaskPriority.HIGH)
        
        self.assertEqual(task.task_id, "test_task")
        self.assertEqual(task.data, {"data": "test"})
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertIsNotNone(task.created_at)
    
    def test_task_priority_comparison(self):
        """测试任务优先级比较"""
        urgent_task = Task("urgent", {}, TaskPriority.URGENT)
        normal_task = Task("normal", {}, TaskPriority.NORMAL)
        
        # 优先级高的任务应该小于优先级低的任务（用于优先级队列）
        self.assertTrue(urgent_task < normal_task)
    
    def test_task_to_dict(self):
        """测试任务字典转换"""
        task = Task("test", {"key": "value"}, TaskPriority.HIGH)
        task_dict = task.to_dict()
        
        self.assertIn('task_id', task_dict)
        self.assertIn('data', task_dict)
        self.assertIn('priority', task_dict)
        self.assertIn('created_at', task_dict)


class TestThreadSyncDemo(unittest.TestCase):
    """线程同步演示测试类"""
    
    def setUp(self):
        self.demo = ThreadSyncDemo()
    
    def test_shared_data_structure(self):
        """测试共享数据结构"""
        self.assertIn('counter', self.demo.shared_data)
        self.assertIn('items', self.demo.shared_data)
        self.assertEqual(self.demo.shared_data['counter'], 0)
        self.assertEqual(len(self.demo.shared_data['items']), 0)


class TestFileDownloader(unittest.TestCase):
    """文件下载器测试类"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = FileDownloader(download_dir=self.temp_dir, max_workers=2)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_download_task_creation(self):
        """测试下载任务创建"""
        url = "https://httpbin.org/bytes/1024"
        task = self.downloader.add_download(url)
        
        self.assertEqual(task.url, url)
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.downloaded_bytes, 0)
        self.assertEqual(task.total_bytes, 0)
    
    def test_download_task_properties(self):
        """测试下载任务属性"""
        task = DownloadTask("http://example.com/file.txt", "test.txt")
        
        self.assertEqual(task.progress, 0.0)
        self.assertEqual(task.duration, 0.0)
        
        # 模拟下载进度
        task.total_bytes = 1000
        task.downloaded_bytes = 500
        self.assertEqual(task.progress, 50.0)
    
    @patch('requests.head')
    @patch('requests.get')
    def test_download_file(self, mock_get, mock_head):
        """测试文件下载功能"""
        # 模拟HTTP响应
        mock_head.return_value.headers = {'content-length': '1024'}
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'test_data']
        mock_get.return_value = mock_response
        
        task = DownloadTask("http://example.com/test.txt")
        result = self.downloader.download_file(task)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('downloaded_bytes', result)


class TestDataProcessor(unittest.TestCase):
    """数据处理器测试类"""
    
    def setUp(self):
        self.processor = DataProcessor(max_workers=2, chunk_size=100)
    
    def test_data_chunk_creation(self):
        """测试数据块创建"""
        test_data = [{'id': i, 'value': i * 2} for i in range(50)]
        chunk = DataChunk("TEST_CHUNK", test_data, len(test_data))
        
        self.assertEqual(chunk.chunk_id, "TEST_CHUNK")
        self.assertEqual(len(chunk), 50)
        self.assertFalse(chunk.processed)
        self.assertIsNone(chunk.result)
    
    def test_data_splitting(self):
        """测试数据分割功能"""
        test_data = [{'id': i} for i in range(250)]
        chunks = self.processor.split_data(test_data)
        
        # 应该分割为3个块（100, 100, 50）
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 100)
        self.assertEqual(len(chunks[1]), 100)
        self.assertEqual(len(chunks[2]), 50)
    
    def test_data_generator_sales_data(self):
        """测试销售数据生成器"""
        sales_data = DataGenerator.generate_sales_data(100)
        
        self.assertEqual(len(sales_data), 100)
        
        # 验证数据结构
        for record in sales_data[:5]:  # 检查前5条
            self.assertIn('id', record)
            self.assertIn('product', record)
            self.assertIn('region', record)
            self.assertIn('quantity', record)
            self.assertIn('unit_price', record)
            self.assertIn('total_amount', record)
    
    def test_data_generator_log_data(self):
        """测试日志数据生成器"""
        log_data = DataGenerator.generate_log_data(100)
        
        self.assertEqual(len(log_data), 100)
        
        # 验证数据结构
        for record in log_data[:5]:  # 检查前5条
            self.assertIn('timestamp', record)
            self.assertIn('level', record)
            self.assertIn('service', record)
            self.assertIn('message', record)
            self.assertIn('response_time', record)


class TestThreadSafety(unittest.TestCase):
    """线程安全测试类"""
    
    def test_counter_thread_safety(self):
        """测试计数器线程安全"""
        counter = {'value': 0}
        lock = threading.Lock()
        
        def increment_with_lock():
            for _ in range(1000):
                with lock:
                    counter['value'] += 1
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=increment_with_lock)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 有锁的情况下应该得到正确结果
        self.assertEqual(counter['value'], 5000)
    
    def test_queue_thread_safety(self):
        """测试队列线程安全"""
        test_queue = queue.Queue()
        items_produced = 100
        items_consumed = []
        
        def producer():
            for i in range(items_produced):
                test_queue.put(f"item_{i}")
        
        def consumer():
            while len(items_consumed) < items_produced:
                try:
                    item = test_queue.get(timeout=1)
                    items_consumed.append(item)
                    test_queue.task_done()
                except queue.Empty:
                    break
        
        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)
        
        producer_thread.start()
        consumer_thread.start()
        
        producer_thread.join()
        consumer_thread.join()
        
        # 验证所有物品都被消费
        self.assertEqual(len(items_consumed), items_produced)


class TestPerformance(unittest.TestCase):
    """性能测试类"""
    
    def test_thread_pool_performance(self):
        """测试线程池性能"""
        import concurrent.futures
        
        def cpu_task(n):
            return sum(i * i for i in range(n))
        
        tasks = [1000] * 10
        
        # 串行执行
        start_time = time.time()
        serial_results = [cpu_task(n) for n in tasks]
        serial_time = time.time() - start_time
        
        # 并行执行
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            parallel_results = list(executor.map(cpu_task, tasks))
        parallel_time = time.time() - start_time
        
        # 验证结果一致性
        self.assertEqual(serial_results, parallel_results)
        
        # 在CPU密集型任务中，由于GIL的存在，并行可能不会显著提升性能
        # 但我们至少验证并行版本可以正常工作
        self.assertGreater(len(parallel_results), 0)
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 创建大量数据
        large_data = [{'id': i, 'data': 'x' * 100} for i in range(10000)]
        
        # 处理数据
        processor = DataProcessor(max_workers=2, chunk_size=1000)
        chunks = processor.split_data(large_data)
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # 清理
        del large_data
        del chunks
        gc.collect()
        
        # 验证内存增长在合理范围内（小于100MB）
        self.assertLess(memory_increase, 100 * 1024 * 1024)


def run_tests():
    """运行所有测试"""
    print("🧪 运行Python多线程演示系统测试套件")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestBasicThreadDemo,
        TestThreadPoolDemo,
        TestProducerConsumerDemo,
        TestThreadSyncDemo,
        TestFileDownloader,
        TestDataProcessor,
        TestThreadSafety,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(test_suite)
    
    # 打印测试摘要
    print(f"\n📊 测试摘要:")
    print(f"  运行测试数: {result.testsRun}")
    print(f"  测试失败: {len(result.failures)}")
    print(f"  测试错误: {len(result.errors)}")
    print(f"  跳过测试: {len(result.skipped)}")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 测试成功率: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)