"""
高级日志系统

提供结构化日志记录和分析功能
"""

import logging
import logging.handlers
import sys
import os
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import queue


class ThreadSafeLogger:
    """线程安全的日志记录器"""
    
    def __init__(self, name: str = "threading_demo", level: str = "INFO", 
                 log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.lock = threading.Lock()
        self.log_records: List[Dict[str, Any]] = []
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers(log_file)
            
    def _setup_handlers(self, log_file: Optional[str]):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 文件处理器
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
        # 自定义格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'
        )
        
        console_handler.setFormatter(formatter)
        if log_file:
            file_handler.setFormatter(formatter)
            
        self.logger.addHandler(console_handler)
        if log_file:
            self.logger.addHandler(file_handler)
            
    def _record_log(self, level: str, message: str, extra_data: Optional[Dict] = None):
        """记录日志到内存"""
        with self.lock:
            record = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'thread_id': threading.get_ident(),
                'thread_name': threading.current_thread().name,
                'extra_data': extra_data or {}
            }
            self.log_records.append(record)
            
            # 限制内存中的日志记录数量
            if len(self.log_records) > 1000:
                self.log_records.pop(0)
                
    def debug(self, message: str, extra_data: Optional[Dict] = None):
        """调试日志"""
        self.logger.debug(message)
        self._record_log('DEBUG', message, extra_data)
        
    def info(self, message: str, extra_data: Optional[Dict] = None):
        """信息日志"""
        self.logger.info(message)
        self._record_log('INFO', message, extra_data)
        
    def warning(self, message: str, extra_data: Optional[Dict] = None):
        """警告日志"""
        self.logger.warning(message)
        self._record_log('WARNING', message, extra_data)
        
    def error(self, message: str, extra_data: Optional[Dict] = None):
        """错误日志"""
        self.logger.error(message)
        self._record_log('ERROR', message, extra_data)
        
    def critical(self, message: str, extra_data: Optional[Dict] = None):
        """严重错误日志"""
        self.logger.critical(message)
        self._record_log('CRITICAL', message, extra_data)
        
    def log_thread_event(self, event_type: str, thread_name: str, 
                        details: Optional[Dict] = None):
        """记录线程事件"""
        message = f"线程事件: {event_type} - {thread_name}"
        extra_data = {
            'event_type': event_type,
            'target_thread': thread_name,
            'details': details or {}
        }
        self.info(message, extra_data)
        
    def get_log_records(self, level: Optional[str] = None, 
                       thread_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取日志记录"""
        with self.lock:
            records = self.log_records.copy()
            
        if level:
            records = [r for r in records if r['level'] == level.upper()]
            
        if thread_name:
            records = [r for r in records if r['thread_name'] == thread_name]
            
        return records
        
    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        with self.lock:
            records = self.log_records.copy()
            
        if not records:
            return {"error": "没有日志记录"}
            
        # 按级别统计
        level_counts = {}
        thread_counts = {}
        
        for record in records:
            level = record['level']
            thread_name = record['thread_name']
            
            level_counts[level] = level_counts.get(level, 0) + 1
            thread_counts[thread_name] = thread_counts.get(thread_name, 0) + 1
            
        return {
            'total_records': len(records),
            'time_range': {
                'start': records[0]['timestamp'],
                'end': records[-1]['timestamp']
            },
            'level_distribution': level_counts,
            'thread_distribution': thread_counts,
            'most_active_thread': max(thread_counts.items(), key=lambda x: x[1])[0] if thread_counts else None
        }
        
    def save_logs_to_file(self, filename: str, format_type: str = 'json'):
        """保存日志到文件"""
        with self.lock:
            records = self.log_records.copy()
            
        try:
            if format_type == 'json':
                data = {
                    'export_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_records': len(records)
                    },
                    'statistics': self.get_log_statistics(),
                    'records': records
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif format_type == 'text':
                with open(filename, 'w', encoding='utf-8') as f:
                    for record in records:
                        f.write(f"[{record['timestamp']}] {record['level']} "
                               f"[{record['thread_name']}] {record['message']}\n")
                        
            self.info(f"日志已导出到: {filename} (格式: {format_type})")
            
        except Exception as e:
            self.error(f"保存日志失败: {e}")


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, logger: ThreadSafeLogger):
        self.logger = logger
        
    def analyze_thread_activity(self) -> Dict[str, Any]:
        """分析线程活动"""
        records = self.logger.get_log_records()
        
        if not records:
            return {"error": "没有日志数据"}
            
        thread_activity = {}
        
        for record in records:
            thread_name = record['thread_name']
            if thread_name not in thread_activity:
                thread_activity[thread_name] = {
                    'total_logs': 0,
                    'levels': {},
                    'first_seen': record['timestamp'],
                    'last_seen': record['timestamp']
                }
                
            activity = thread_activity[thread_name]
            activity['total_logs'] += 1
            
            level = record['level']
            activity['levels'][level] = activity['levels'].get(level, 0) + 1
            
            # 更新时间范围
            if record['timestamp'] > activity['last_seen']:
                activity['last_seen'] = record['timestamp']
                
        return thread_activity
        
    def find_error_patterns(self) -> List[Dict[str, Any]]:
        """查找错误模式"""
        error_records = self.logger.get_log_records(level='ERROR')
        warning_records = self.logger.get_log_records(level='WARNING')
        
        patterns = []
        
        # 分析错误频率
        error_threads = {}
        for record in error_records:
            thread_name = record['thread_name']
            error_threads[thread_name] = error_threads.get(thread_name, 0) + 1
            
        if error_threads:
            patterns.append({
                'type': 'error_frequency',
                'description': '线程错误频率分析',
                'data': error_threads
            })
            
        # 分析警告模式
        warning_threads = {}
        for record in warning_records:
            thread_name = record['thread_name']
            warning_threads[thread_name] = warning_threads.get(thread_name, 0) + 1
            
        if warning_threads:
            patterns.append({
                'type': 'warning_frequency',
                'description': '线程警告频率分析',
                'data': warning_threads
            })
            
        return patterns
        
    def create_activity_report(self) -> str:
        """创建活动报告"""
        stats = self.logger.get_log_statistics()
        activity = self.analyze_thread_activity()
        patterns = self.find_error_patterns()
        
        report = []
        report.append("=== 日志活动分析报告 ===")
        
        if 'error' not in stats:
            report.append(f"总日志记录: {stats['total_records']}")
            report.append(f"时间范围: {stats['time_range']['start']} 到 {stats['time_range']['end']}")
            report.append("")
            
            report.append("日志级别分布:")
            for level, count in stats['level_distribution'].items():
                report.append(f"  {level}: {count}")
            report.append("")
            
            report.append("线程活动分析:")
            if 'error' not in activity:
                for thread_name, data in activity.items():
                    report.append(f"  线程 {thread_name}:")
                    report.append(f"    总日志: {data['total_logs']}")
                    report.append(f"    级别分布: {data['levels']}")
                report.append("")
                
            if patterns:
                report.append("错误模式分析:")
                for pattern in patterns:
                    report.append(f"  {pattern['description']}:")
                    for item, count in pattern['data'].items():
                        report.append(f"    {item}: {count}")
                    
        return "\n".join(report)


class LoggingDemo:
    """日志系统演示"""
    
    def __init__(self):
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = ThreadSafeLogger(
            name="demo_logger",
            level="DEBUG",
            log_file="logs/threading_demo.log"
        )
        self.analyzer = LogAnalyzer(self.logger)
        
    def demo_basic_logging(self):
        """基础日志演示"""
        print("\n=== 基础日志系统演示 ===")
        
        def worker_with_logging(worker_id: int):
            """带日志的工作线程"""
            self.logger.log_thread_event("THREAD_START", f"Worker{worker_id}")
            
            try:
                self.logger.info(f"Worker{worker_id} 开始工作")
                
                for i in range(5):
                    self.logger.debug(f"Worker{worker_id} 执行步骤 {i+1}")
                    time.sleep(0.5)
                    
                    # 模拟偶尔的警告
                    if i == 2 and worker_id == 2:
                        self.logger.warning(f"Worker{worker_id} 遇到轻微问题")
                        
                self.logger.info(f"Worker{worker_id} 工作完成")
                
            except Exception as e:
                self.logger.error(f"Worker{worker_id} 执行失败: {e}")
            finally:
                self.logger.log_thread_event("THREAD_END", f"Worker{worker_id}")
                
        # 创建工作线程
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=worker_with_logging,
                args=(i+1,),
                name=f"LogWorker{i+1}"
            )
            threads.append(thread)
            
        self.logger.info("开始基础日志演示")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        self.logger.info("基础日志演示完成")
        
        # 显示统计信息
        print("\n日志统计信息:")
        stats = self.logger.get_log_statistics()
        print(f"  总记录数: {stats['total_records']}")
        print(f"  级别分布: {stats['level_distribution']}")
        print(f"  线程分布: {stats['thread_distribution']}")
        
    def demo_error_logging(self):
        """错误日志演示"""
        print("\n=== 错误日志处理演示 ===")
        
        def problematic_worker(worker_id: int):
            """可能出现问题的工作线程"""
            self.logger.info(f"ProblematicWorker{worker_id} 启动")
            
            try:
                if worker_id == 1:
                    # 模拟运行时错误
                    raise RuntimeError(f"Worker{worker_id} 模拟运行时错误")
                elif worker_id == 2:
                    # 模拟值错误
                    raise ValueError(f"Worker{worker_id} 模拟值错误")
                else:
                    self.logger.info(f"ProblematicWorker{worker_id} 正常完成")
                    
            except Exception as e:
                self.logger.error(f"ProblematicWorker{worker_id} 异常: {e}", {
                    'exception_type': type(e).__name__,
                    'worker_id': worker_id
                })
                
        # 创建问题线程
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=problematic_worker,
                args=(i+1,),
                name=f"ProblematicWorker{i+1}"
            )
            threads.append(thread)
            
        self.logger.info("开始错误日志演示")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        # 分析错误模式
        print("\n错误模式分析:")
        patterns = self.analyzer.find_error_patterns()
        for pattern in patterns:
            print(f"  {pattern['description']}: {pattern['data']}")
            
    def run_all_demos(self):
        """运行所有日志演示"""
        print("开始日志系统演示...")
        
        try:
            self.demo_basic_logging()
            time.sleep(1)
            
            self.demo_error_logging()
            time.sleep(1)
            
            # 生成并显示报告
            print("\n" + self.analyzer.create_activity_report())
            
            # 保存日志
            self.logger.save_logs_to_file("logs/demo_logs.json", "json")
            
        except KeyboardInterrupt:
            print("\n日志演示被用户中断")
        except Exception as e:
            print(f"\n日志演示出错: {e}")
        finally:
            self.logger.info("日志系统演示结束")


def main():
    """主函数"""
    demo = LoggingDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()