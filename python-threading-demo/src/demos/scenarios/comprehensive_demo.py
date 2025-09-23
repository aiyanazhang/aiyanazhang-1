"""
综合演示场景
"""

import threading
import time
import random
import queue
import math
from concurrent.futures import ThreadPoolExecutor


class ComprehensiveDemo:
    """综合演示场景"""
    
    def demo_concurrent_calculation(self):
        """并发计算演示 - 计算质数"""
        print("\n=== 并发计算演示 ===")
        print("使用多线程计算大范围内的质数")
        
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
            
        def find_primes_in_range(start, end, result_queue, thread_name):
            """在指定范围内查找质数"""
            primes = []
            for num in range(start, end + 1):
                if is_prime(num):
                    primes.append(num)
            result_queue.put((thread_name, len(primes), primes[:10]))  # 只保存前10个作为示例
            print(f"[{thread_name}] 范围 {start}-{end}: 找到 {len(primes)} 个质数")
            
        # 计算范围
        total_range = 10000
        num_threads = 4
        range_size = total_range // num_threads
        
        result_queue = queue.Queue()
        threads = []
        
        print(f"将 1-{total_range} 的范围分配给 {num_threads} 个线程")
        
        start_time = time.time()
        
        # 创建线程计算不同范围
        for i in range(num_threads):
            start = i * range_size + 1
            end = (i + 1) * range_size if i < num_threads - 1 else total_range
            
            thread = threading.Thread(
                target=find_primes_in_range,
                args=(start, end, result_queue, f"CalcThread{i+1}"),
                name=f"Calculator{i+1}"
            )
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        
        # 收集结果
        total_primes = 0
        print("\n计算结果:")
        while not result_queue.empty():
            thread_name, count, sample_primes = result_queue.get()
            total_primes += count
            print(f"  {thread_name}: {count} 个质数，示例: {sample_primes}")
            
        print(f"\n总计找到 {total_primes} 个质数")
        print(f"并发计算耗时: {end_time - start_time:.2f} 秒")
        
    def demo_producer_consumer_system(self):
        """生产者-消费者系统演示"""
        print("\n=== 生产者-消费者系统演示 ===")
        print("模拟数据处理管道")
        
        # 多级处理队列
        raw_data_queue = queue.Queue(maxsize=10)
        processed_data_queue = queue.Queue(maxsize=10)
        final_results = []
        results_lock = threading.Lock()
        
        # 控制运行的事件
        stop_event = threading.Event()
        
        def data_producer(producer_id):
            """数据生产者"""
            count = 0
            while not stop_event.is_set() and count < 15:
                data = {
                    'id': f"data_{producer_id}_{count}",
                    'value': random.randint(1, 100),
                    'timestamp': time.time()
                }
                try:
                    raw_data_queue.put(data, timeout=1)
                    print(f"[Producer{producer_id}] 生产数据: {data['id']}")
                    count += 1
                    time.sleep(random.uniform(0.3, 0.8))
                except queue.Full:
                    print(f"[Producer{producer_id}] 队列满，跳过数据")
                    
        def data_processor(processor_id):
            """数据处理器"""
            while not stop_event.is_set():
                try:
                    data = raw_data_queue.get(timeout=2)
                    
                    # 模拟数据处理
                    processed_value = data['value'] * 2 + random.randint(1, 10)
                    processed_data = {
                        'original_id': data['id'],
                        'processed_value': processed_value,
                        'processor': f"Processor{processor_id}",
                        'process_time': time.time()
                    }
                    
                    processed_data_queue.put(processed_data)
                    print(f"[Processor{processor_id}] 处理完成: {data['id']} -> {processed_value}")
                    
                    raw_data_queue.task_done()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except queue.Empty:
                    continue
                    
        def result_collector():
            """结果收集器"""
            while not stop_event.is_set():
                try:
                    processed_data = processed_data_queue.get(timeout=2)
                    
                    with results_lock:
                        final_results.append(processed_data)
                        
                    print(f"[Collector] 收集结果: {processed_data['original_id']}")
                    processed_data_queue.task_done()
                    
                except queue.Empty:
                    continue
                    
        # 创建线程
        threads = []
        
        # 2个生产者
        for i in range(2):
            thread = threading.Thread(target=data_producer, args=(i+1,), name=f"Producer{i+1}")
            threads.append(thread)
            
        # 3个处理器
        for i in range(3):
            thread = threading.Thread(target=data_processor, args=(i+1,), name=f"Processor{i+1}")
            threads.append(thread)
            
        # 1个收集器
        collector_thread = threading.Thread(target=result_collector, name="Collector")
        threads.append(collector_thread)
        
        print("启动生产者-消费者处理管道...")
        
        # 启动所有线程
        for thread in threads:
            thread.start()
            
        # 运行一段时间
        time.sleep(10)
        
        # 停止系统
        print("\n停止生产者-消费者系统...")
        stop_event.set()
        
        # 等待线程完成
        for thread in threads:
            thread.join(timeout=3)
            
        print(f"\n系统运行结果:")
        print(f"  原始数据队列剩余: {raw_data_queue.qsize()}")
        print(f"  处理数据队列剩余: {processed_data_queue.qsize()}")
        print(f"  最终收集结果数: {len(final_results)}")
        
    def demo_web_crawler_simulation(self):
        """网络爬虫模拟演示"""
        print("\n=== 网络爬虫模拟演示 ===")
        print("模拟多线程网络爬虫")
        
        # 模拟URL队列
        urls_to_crawl = [f"http://example.com/page{i}" for i in range(1, 21)]
        url_queue = queue.Queue()
        results = []
        results_lock = threading.Lock()
        
        # 添加URL到队列
        for url in urls_to_crawl:
            url_queue.put(url)
            
        def web_crawler(crawler_id):
            """网络爬虫工作线程"""
            while True:
                try:
                    url = url_queue.get(timeout=1)
                    
                    # 模拟网络请求
                    print(f"[Crawler{crawler_id}] 正在爬取: {url}")
                    crawl_time = random.uniform(1, 3)  # 模拟网络延迟
                    time.sleep(crawl_time)
                    
                    # 模拟抓取结果
                    page_data = {
                        'url': url,
                        'title': f"Page Title for {url.split('/')[-1]}",
                        'content_length': random.randint(1000, 10000),
                        'links_found': random.randint(5, 50),
                        'crawl_time': crawl_time,
                        'crawler': f"Crawler{crawler_id}"
                    }
                    
                    with results_lock:
                        results.append(page_data)
                        
                    print(f"[Crawler{crawler_id}] 完成爬取: {url} (耗时: {crawl_time:.1f}s)")
                    url_queue.task_done()
                    
                except queue.Empty:
                    print(f"[Crawler{crawler_id}] 没有更多URL，退出")
                    break
                except Exception as e:
                    print(f"[Crawler{crawler_id}] 爬取错误: {e}")
                    
        # 使用线程池
        print(f"开始爬取 {len(urls_to_crawl)} 个URL...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5, thread_name_prefix="Crawler") as executor:
            # 提交爬虫任务
            futures = []
            for i in range(5):
                future = executor.submit(web_crawler, i+1)
                futures.append(future)
                
            # 等待所有任务完成
            for future in futures:
                future.result()
                
        end_time = time.time()
        
        print(f"\n爬虫运行结果:")
        print(f"  成功爬取页面数: {len(results)}")
        print(f"  总耗时: {end_time - start_time:.2f} 秒")
        
        # 统计信息
        total_content = sum(r['content_length'] for r in results)
        total_links = sum(r['links_found'] for r in results)
        avg_time = sum(r['crawl_time'] for r in results) / len(results) if results else 0
        
        print(f"  总内容长度: {total_content:,} 字符")
        print(f"  总链接数: {total_links}")
        print(f"  平均爬取时间: {avg_time:.2f} 秒/页面")
        
    def run_all_demos(self):
        """运行所有综合演示"""
        print("开始综合演示场景...")
        
        try:
            self.demo_concurrent_calculation()
            time.sleep(2)
            
            self.demo_producer_consumer_system()
            time.sleep(2)
            
            self.demo_web_crawler_simulation()
            
        except KeyboardInterrupt:
            print("\n综合演示被用户中断")
        except Exception as e:
            print(f"\n综合演示出错: {e}")
        finally:
            print("\n综合演示场景结束")


def main():
    demo = ComprehensiveDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()