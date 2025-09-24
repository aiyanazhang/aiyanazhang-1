"""
数据处理器实际应用场景演示
大数据集并行处理，展示多线程在数据处理中的应用
"""

import threading
import time
import random
import csv
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Tuple
import concurrent.futures
import queue
from collections import defaultdict
import math


class DataChunk:
    """数据块类"""
    
    def __init__(self, chunk_id: str, data: List[Dict[str, Any]], chunk_size: int):
        self.chunk_id = chunk_id
        self.data = data
        self.chunk_size = chunk_size
        self.processed = False
        self.result: Optional[Dict[str, Any]] = None
        self.processing_time: float = 0.0
        self.error: Optional[str] = None
        
    def __len__(self):
        return len(self.data)


class DataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_sales_data(count: int) -> List[Dict[str, Any]]:
        """生成销售数据"""
        products = ['笔记本电脑', '手机', '平板电脑', '耳机', '键盘', '鼠标', '显示器', '音响']
        regions = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安']
        
        data = []
        base_date = datetime(2023, 1, 1)
        
        for i in range(count):
            record = {
                'id': f"ORDER_{i+1:06d}",
                'product': random.choice(products),
                'region': random.choice(regions),
                'quantity': random.randint(1, 100),
                'unit_price': round(random.uniform(100, 5000), 2),
                'date': (base_date + timedelta(days=random.randint(0, 365))).isoformat(),
                'customer_id': f"CUST_{random.randint(1, 10000):05d}",
                'sales_person': f"SALES_{random.randint(1, 50):03d}"
            }
            record['total_amount'] = record['quantity'] * record['unit_price']
            data.append(record)
        
        return data
    
    @staticmethod
    def generate_log_data(count: int) -> List[Dict[str, Any]]:
        """生成日志数据"""
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        services = ['user-service', 'order-service', 'payment-service', 'inventory-service']
        
        data = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(count):
            record = {
                'timestamp': (base_time + timedelta(
                    seconds=random.randint(0, 7*24*3600)
                )).isoformat(),
                'level': random.choice(log_levels),
                'service': random.choice(services),
                'message': f"Operation {i+1} executed",
                'user_id': random.randint(1, 1000),
                'session_id': f"SESSION_{random.randint(1, 5000):05d}",
                'response_time': random.randint(10, 2000),  # ms
                'status_code': random.choice([200, 201, 400, 404, 500])
            }
            data.append(record)
        
        return data


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self, max_workers: int = 4, chunk_size: int = 1000):
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.processing_stats = {
            'total_records': 0,
            'processed_records': 0,
            'chunks_processed': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
        self.stats_lock = threading.Lock()
        
        print(f"🔧 数据处理器配置:")
        print(f"   最大工作线程: {max_workers}")
        print(f"   数据块大小: {chunk_size}")
    
    def split_data(self, data: List[Dict[str, Any]]) -> List[DataChunk]:
        """将数据分割成块"""
        chunks = []
        total_records = len(data)
        
        for i in range(0, total_records, self.chunk_size):
            chunk_data = data[i:i + self.chunk_size]
            chunk_id = f"CHUNK_{len(chunks)+1:03d}"
            chunk = DataChunk(chunk_id, chunk_data, len(chunk_data))
            chunks.append(chunk)
        
        print(f"📊 数据分割完成: {total_records:,} 条记录 → {len(chunks)} 个数据块")
        return chunks
    
    def process_sales_analytics(self, chunk: DataChunk) -> Dict[str, Any]:
        """处理销售数据分析"""
        start_time = time.time()
        
        try:
            print(f"[{threading.current_thread().name}] 开始处理 {chunk.chunk_id} ({len(chunk)} 条记录)")
            
            # 模拟复杂的数据处理
            time.sleep(random.uniform(0.5, 1.5))
            
            # 计算统计信息
            total_amount = sum(record['total_amount'] for record in chunk.data)
            total_quantity = sum(record['quantity'] for record in chunk.data)
            
            # 按产品分组统计
            product_stats = defaultdict(lambda: {'quantity': 0, 'amount': 0, 'orders': 0})
            for record in chunk.data:
                product = record['product']
                product_stats[product]['quantity'] += record['quantity']
                product_stats[product]['amount'] += record['total_amount']
                product_stats[product]['orders'] += 1
            
            # 按地区分组统计
            region_stats = defaultdict(lambda: {'quantity': 0, 'amount': 0, 'orders': 0})
            for record in chunk.data:
                region = record['region']
                region_stats[region]['quantity'] += record['quantity']
                region_stats[region]['amount'] += record['total_amount']
                region_stats[region]['orders'] += 1
            
            # 计算平均值
            avg_order_value = total_amount / len(chunk.data) if chunk.data else 0
            avg_quantity = total_quantity / len(chunk.data) if chunk.data else 0
            
            result = {
                'chunk_id': chunk.chunk_id,
                'record_count': len(chunk.data),
                'total_amount': total_amount,
                'total_quantity': total_quantity,
                'avg_order_value': avg_order_value,
                'avg_quantity': avg_quantity,
                'product_stats': dict(product_stats),
                'region_stats': dict(region_stats),
                'processing_thread': threading.current_thread().name
            }
            
            chunk.result = result
            chunk.processed = True
            chunk.processing_time = time.time() - start_time
            
            print(f"[{threading.current_thread().name}] ✅ {chunk.chunk_id} 处理完成 "
                  f"(耗时: {chunk.processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            chunk.error = str(e)
            chunk.processing_time = time.time() - start_time
            print(f"[{threading.current_thread().name}] ❌ {chunk.chunk_id} 处理失败: {e}")
            raise
    
    def process_log_analytics(self, chunk: DataChunk) -> Dict[str, Any]:
        """处理日志数据分析"""
        start_time = time.time()
        
        try:
            print(f"[{threading.current_thread().name}] 开始分析 {chunk.chunk_id} ({len(chunk)} 条日志)")
            
            # 模拟日志分析处理
            time.sleep(random.uniform(0.3, 1.0))
            
            # 统计各种指标
            level_counts = defaultdict(int)
            service_counts = defaultdict(int)
            status_counts = defaultdict(int)
            response_times = []
            error_logs = []
            
            for record in chunk.data:
                level_counts[record['level']] += 1
                service_counts[record['service']] += 1
                status_counts[record['status_code']] += 1
                response_times.append(record['response_time'])
                
                if record['level'] == 'ERROR':
                    error_logs.append(record)
            
            # 计算响应时间统计
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            
            result = {
                'chunk_id': chunk.chunk_id,
                'log_count': len(chunk.data),
                'level_distribution': dict(level_counts),
                'service_distribution': dict(service_counts),
                'status_distribution': dict(status_counts),
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'error_count': len(error_logs),
                'processing_thread': threading.current_thread().name
            }
            
            chunk.result = result
            chunk.processed = True
            chunk.processing_time = time.time() - start_time
            
            print(f"[{threading.current_thread().name}] ✅ {chunk.chunk_id} 分析完成 "
                  f"(耗时: {chunk.processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            chunk.error = str(e)
            chunk.processing_time = time.time() - start_time
            print(f"[{threading.current_thread().name}] ❌ {chunk.chunk_id} 分析失败: {e}")
            raise
    
    def parallel_processing(self, data: List[Dict[str, Any]], 
                          processor_func: Callable[[DataChunk], Dict[str, Any]]) -> Dict[str, Any]:
        """并行处理数据"""
        self.processing_stats['total_records'] = len(data)
        self.processing_stats['start_time'] = time.time()
        
        print(f"\n🚀 开始并行处理 {len(data):,} 条数据")
        print("=" * 60)
        
        # 分割数据
        chunks = self.split_data(data)
        
        # 并行处理
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有处理任务
            future_to_chunk = {
                executor.submit(processor_func, chunk): chunk 
                for chunk in chunks
            }
            
            # 收集结果
            completed_chunks = 0
            total_chunks = len(chunks)
            
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed_chunks += 1
                    
                    with self.stats_lock:
                        self.processing_stats['processed_records'] += len(chunk)
                        self.processing_stats['chunks_processed'] += 1
                    
                    progress = (completed_chunks / total_chunks) * 100
                    print(f"📊 处理进度: {completed_chunks}/{total_chunks} ({progress:.1f}%)")
                    
                except Exception as e:
                    with self.stats_lock:
                        self.processing_stats['errors'].append({
                            'chunk_id': chunk.chunk_id,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
                    print(f"❌ 块处理失败: {chunk.chunk_id} - {e}")
        
        self.processing_stats['end_time'] = time.time()
        
        # 聚合结果
        aggregated_result = self._aggregate_results(results, chunks)
        
        # 打印统计信息
        self._print_processing_summary(chunks)
        
        return aggregated_result
    
    def _aggregate_results(self, results: List[Dict[str, Any]], 
                          chunks: List[DataChunk]) -> Dict[str, Any]:
        """聚合处理结果"""
        if not results:
            return {}
        
        # 检查结果类型
        if 'total_amount' in results[0]:
            return self._aggregate_sales_results(results)
        elif 'log_count' in results[0]:
            return self._aggregate_log_results(results)
        else:
            return {'message': '未知的结果类型'}
    
    def _aggregate_sales_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合销售数据结果"""
        total_amount = sum(r['total_amount'] for r in results)
        total_quantity = sum(r['total_quantity'] for r in results)
        total_records = sum(r['record_count'] for r in results)
        
        # 聚合产品统计
        global_product_stats = defaultdict(lambda: {'quantity': 0, 'amount': 0, 'orders': 0})
        for result in results:
            for product, stats in result['product_stats'].items():
                global_product_stats[product]['quantity'] += stats['quantity']
                global_product_stats[product]['amount'] += stats['amount']
                global_product_stats[product]['orders'] += stats['orders']
        
        # 聚合地区统计
        global_region_stats = defaultdict(lambda: {'quantity': 0, 'amount': 0, 'orders': 0})
        for result in results:
            for region, stats in result['region_stats'].items():
                global_region_stats[region]['quantity'] += stats['quantity']
                global_region_stats[region]['amount'] += stats['amount']
                global_region_stats[region]['orders'] += stats['orders']
        
        # 找出销量最高的产品和地区
        top_product = max(global_product_stats.items(), key=lambda x: x[1]['amount'])
        top_region = max(global_region_stats.items(), key=lambda x: x[1]['amount'])
        
        return {
            'summary': {
                'total_records': total_records,
                'total_amount': total_amount,
                'total_quantity': total_quantity,
                'avg_order_value': total_amount / total_records if total_records > 0 else 0,
                'avg_quantity': total_quantity / total_records if total_records > 0 else 0
            },
            'top_performers': {
                'product': {'name': top_product[0], 'stats': top_product[1]},
                'region': {'name': top_region[0], 'stats': top_region[1]}
            },
            'product_analysis': dict(global_product_stats),
            'region_analysis': dict(global_region_stats),
            'chunks_processed': len(results)
        }
    
    def _aggregate_log_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """聚合日志数据结果"""
        total_logs = sum(r['log_count'] for r in results)
        total_errors = sum(r['error_count'] for r in results)
        
        # 聚合各种分布
        global_level_dist = defaultdict(int)
        global_service_dist = defaultdict(int)
        global_status_dist = defaultdict(int)
        
        all_response_times = []
        
        for result in results:
            for level, count in result['level_distribution'].items():
                global_level_dist[level] += count
            
            for service, count in result['service_distribution'].items():
                global_service_dist[service] += count
            
            for status, count in result['status_distribution'].items():
                global_status_dist[status] += count
            
            # 收集响应时间（这里简化处理，实际应该从原始数据计算）
            all_response_times.extend([
                result['avg_response_time'],
                result['max_response_time'],
                result['min_response_time']
            ])
        
        global_avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        
        return {
            'summary': {
                'total_logs': total_logs,
                'total_errors': total_errors,
                'error_rate': (total_errors / total_logs * 100) if total_logs > 0 else 0,
                'avg_response_time': global_avg_response_time
            },
            'distributions': {
                'log_levels': dict(global_level_dist),
                'services': dict(global_service_dist),
                'status_codes': dict(global_status_dist)
            },
            'chunks_processed': len(results)
        }
    
    def _print_processing_summary(self, chunks: List[DataChunk]):
        """打印处理摘要"""
        total_time = self.processing_stats['end_time'] - self.processing_stats['start_time']
        
        successful_chunks = [c for c in chunks if c.processed and not c.error]
        failed_chunks = [c for c in chunks if c.error]
        
        total_processing_time = sum(c.processing_time for c in successful_chunks)
        avg_processing_time = total_processing_time / len(successful_chunks) if successful_chunks else 0
        
        throughput = self.processing_stats['total_records'] / total_time if total_time > 0 else 0
        
        print(f"\n📊 数据处理摘要:")
        print(f"  总记录数: {self.processing_stats['total_records']:,}")
        print(f"  处理记录数: {self.processing_stats['processed_records']:,}")
        print(f"  成功块数: {len(successful_chunks)}")
        print(f"  失败块数: {len(failed_chunks)}")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  平均块处理时间: {avg_processing_time:.2f}秒")
        print(f"  吞吐量: {throughput:.2f} 记录/秒")
        
        if self.max_workers > 1:
            theoretical_time = total_processing_time
            parallel_efficiency = (theoretical_time / total_time) / self.max_workers if total_time > 0 else 0
            print(f"  并行效率: {parallel_efficiency:.1%}")
        
        if failed_chunks:
            print(f"\n❌ 失败的数据块:")
            for chunk in failed_chunks[:3]:  # 只显示前3个
                print(f"    {chunk.chunk_id}: {chunk.error}")


def demo_sales_data_processing():
    """销售数据处理演示"""
    print("🛒 销售数据处理演示")
    print("=" * 60)
    
    # 生成测试数据
    print("📊 生成销售测试数据...")
    sales_data = DataGenerator.generate_sales_data(10000)  # 1万条销售记录
    
    # 创建数据处理器
    processor = DataProcessor(max_workers=4, chunk_size=1500)
    
    # 并行处理销售数据
    result = processor.parallel_processing(sales_data, processor.process_sales_analytics)
    
    # 显示分析结果
    print(f"\n📈 销售数据分析结果:")
    summary = result.get('summary', {})
    print(f"  总订单数: {summary.get('total_records', 0):,}")
    print(f"  总销售额: ¥{summary.get('total_amount', 0):,.2f}")
    print(f"  总销量: {summary.get('total_quantity', 0):,}")
    print(f"  平均订单价值: ¥{summary.get('avg_order_value', 0):.2f}")
    
    top_performers = result.get('top_performers', {})
    if top_performers:
        top_product = top_performers.get('product', {})
        top_region = top_performers.get('region', {})
        
        print(f"\n🏆 销售冠军:")
        print(f"  最佳产品: {top_product.get('name')} (销售额: ¥{top_product.get('stats', {}).get('amount', 0):,.2f})")
        print(f"  最佳地区: {top_region.get('name')} (销售额: ¥{top_region.get('stats', {}).get('amount', 0):,.2f})")


def demo_log_data_processing():
    """日志数据处理演示"""
    print(f"\n📋 日志数据处理演示")
    print("=" * 60)
    
    # 生成测试数据
    print("📊 生成日志测试数据...")
    log_data = DataGenerator.generate_log_data(50000)  # 5万条日志记录
    
    # 创建数据处理器
    processor = DataProcessor(max_workers=6, chunk_size=2000)
    
    # 并行处理日志数据
    result = processor.parallel_processing(log_data, processor.process_log_analytics)
    
    # 显示分析结果
    print(f"\n📈 日志分析结果:")
    summary = result.get('summary', {})
    print(f"  总日志数: {summary.get('total_logs', 0):,}")
    print(f"  错误日志数: {summary.get('total_errors', 0):,}")
    print(f"  错误率: {summary.get('error_rate', 0):.2f}%")
    print(f"  平均响应时间: {summary.get('avg_response_time', 0):.2f}ms")
    
    distributions = result.get('distributions', {})
    if distributions:
        print(f"\n📊 日志分布:")
        
        log_levels = distributions.get('log_levels', {})
        print(f"  日志级别分布:")
        for level, count in sorted(log_levels.items()):
            percentage = (count / summary.get('total_logs', 1)) * 100
            print(f"    {level}: {count:,} ({percentage:.1f}%)")
        
        services = distributions.get('services', {})
        print(f"  服务分布:")
        for service, count in sorted(services.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / summary.get('total_logs', 1)) * 100
            print(f"    {service}: {count:,} ({percentage:.1f}%)")


def main():
    """主函数"""
    print("🚀 数据处理器实际应用演示")
    print("=" * 80)
    
    try:
        demo_sales_data_processing()
        demo_log_data_processing()
        
        print(f"\n{'='*80}")
        print("✅ 数据处理器演示完成")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()