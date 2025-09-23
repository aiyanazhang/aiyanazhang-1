"""
执行引擎模块
在Docker容器中执行命令并收集结果，提供完整的执行管理功能
"""

import time
import logging
import threading
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from .command_parser import ParsedCommand, CommandHistory
from .parameter_validator import ParameterValidator, ValidationResult
from .docker_manager import DockerManager, ExecutionResult
from .config_manager import ConfigManager


@dataclass
class ExecutionContext:
    """执行上下文"""
    command: ParsedCommand
    validation_result: ValidationResult
    start_time: datetime
    mount_path: Optional[str] = None
    execution_id: str = field(default_factory=lambda: f"exec_{int(time.time() * 1000)}")
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    """执行指标"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    validation_failures: int = 0
    docker_failures: int = 0
    timeout_failures: int = 0
    
    def update(self, result: ExecutionResult, validation_failed: bool = False, 
               docker_failed: bool = False, timeout_failed: bool = False):
        """更新指标"""
        self.total_executions += 1
        
        if validation_failed:
            self.validation_failures += 1
        elif docker_failed:
            self.docker_failures += 1
        elif timeout_failed:
            self.timeout_failures += 1
        elif result.success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        if hasattr(result, 'execution_time'):
            self.total_execution_time += result.execution_time
            self.average_execution_time = self.total_execution_time / self.total_executions


class ExecutionMonitor:
    """执行监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.execution_history: List[ExecutionContext] = []
        self.metrics = ExecutionMetrics()
        self._lock = threading.Lock()
        
        # 监控阈值
        self.max_execution_time = 300  # 5分钟
        self.max_concurrent_executions = 10
        self.max_history_size = 1000
    
    def start_execution(self, context: ExecutionContext):
        """开始执行监控"""
        with self._lock:
            if len(self.active_executions) >= self.max_concurrent_executions:
                raise RuntimeError("并发执行数量已达上限")
            
            self.active_executions[context.execution_id] = context
            self.logger.info(f"开始监控执行: {context.execution_id}")
    
    def finish_execution(self, execution_id: str, result: ExecutionResult):
        """完成执行监控"""
        with self._lock:
            context = self.active_executions.pop(execution_id, None)
            if context:
                context.metadata['result'] = result
                context.metadata['end_time'] = datetime.now()
                
                # 添加到历史记录
                self.execution_history.append(context)
                
                # 保持历史记录大小
                if len(self.execution_history) > self.max_history_size:
                    self.execution_history.pop(0)
                
                # 更新指标
                self.metrics.update(result)
                
                self.logger.info(f"完成执行监控: {execution_id}, 成功: {result.success}")
    
    def get_active_executions(self) -> List[ExecutionContext]:
        """获取活动执行"""
        with self._lock:
            return list(self.active_executions.values())
    
    def get_execution_metrics(self) -> ExecutionMetrics:
        """获取执行指标"""
        return self.metrics
    
    def check_timeouts(self) -> List[str]:
        """检查超时的执行"""
        current_time = datetime.now()
        timeout_executions = []
        
        with self._lock:
            for execution_id, context in self.active_executions.items():
                execution_time = (current_time - context.start_time).total_seconds()
                if execution_time > self.max_execution_time:
                    timeout_executions.append(execution_id)
        
        return timeout_executions


class ExecutionEngine:
    """执行引擎主类"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.validator = ParameterValidator(config_manager.security_config)
        self.docker_manager = DockerManager(
            config_manager.docker_config,
            config_manager.security_config
        )
        self.command_history = CommandHistory()
        self.execution_monitor = ExecutionMonitor()
        
        # 执行钩子
        self.before_execution_hooks: List[Callable[[ExecutionContext], None]] = []
        self.after_execution_hooks: List[Callable[[ExecutionContext, ExecutionResult], None]] = []
        
        # 初始化状态
        self._initialized = False
        self._shutdown = False
        
        # 启动监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def initialize(self) -> bool:
        """初始化执行引擎"""
        if self._initialized:
            return True
        
        try:
            # 初始化Docker管理器
            if not self.docker_manager.initialize():
                self.logger.error("Docker管理器初始化失败")
                return False
            
            # 验证配置
            if not self.config_manager.validate_config():
                self.logger.error("配置验证失败")
                return False
            
            self._initialized = True
            self.logger.info("执行引擎初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"执行引擎初始化失败: {e}")
            return False
    
    def execute(self, parsed_command: ParsedCommand, mount_path: Optional[str] = None) -> ExecutionResult:
        """执行命令"""
        if not self._initialized:
            if not self.initialize():
                return self._create_error_result("执行引擎未初始化")
        
        if self._shutdown:
            return self._create_error_result("执行引擎已关闭")
        
        # 创建执行上下文
        context = ExecutionContext(
            command=parsed_command,
            validation_result=None,
            start_time=datetime.now(),
            mount_path=mount_path
        )
        
        try:
            # 开始监控
            self.execution_monitor.start_execution(context)
            
            # 执行前钩子
            for hook in self.before_execution_hooks:
                try:
                    hook(context)
                except Exception as e:
                    self.logger.warning(f"执行前钩子失败: {e}")
            
            # 验证命令
            self.logger.info(f"开始验证命令: {parsed_command.command}")
            validation_result = self.validator.validate(parsed_command)
            context.validation_result = validation_result
            
            if not validation_result.is_valid:
                result = self._create_validation_error_result(validation_result)
                self.execution_monitor.metrics.update(result, validation_failed=True)
                return result
            
            # 记录警告
            if validation_result.warnings:
                self.logger.warning(f"命令验证警告: {validation_result.warnings}")
            
            # 执行命令
            self.logger.info(f"开始执行命令: {parsed_command.command}")
            result = self.docker_manager.execute_command(parsed_command, mount_path)
            
            # 记录命令历史
            self.command_history.add(parsed_command)
            
            # 记录执行结果
            if result.success:
                self.logger.info(f"命令执行成功: {parsed_command.command}, 耗时: {result.execution_time:.2f}s")
            else:
                self.logger.error(f"命令执行失败: {parsed_command.command}, 错误: {result.stderr}")
            
            return result
            
        except Exception as e:
            error_msg = f"执行过程中发生错误: {e}"
            self.logger.error(error_msg)
            result = self._create_error_result(error_msg)
            self.execution_monitor.metrics.update(result, docker_failed=True)
            return result
            
        finally:
            # 完成监控
            if 'result' in locals():
                self.execution_monitor.finish_execution(context.execution_id, result)
            
            # 执行后钩子
            for hook in self.after_execution_hooks:
                try:
                    hook(context, result if 'result' in locals() else None)
                except Exception as e:
                    self.logger.warning(f"执行后钩子失败: {e}")
    
    def execute_batch(self, commands: List[ParsedCommand], mount_path: Optional[str] = None) -> List[ExecutionResult]:
        """批量执行命令"""
        results = []
        
        for i, command in enumerate(commands):
            self.logger.info(f"执行批量命令 {i+1}/{len(commands)}: {command.command}")
            result = self.execute(command, mount_path)
            results.append(result)
            
            # 如果命令失败且不是验证错误，可以选择继续或停止
            if not result.success and "验证失败" not in (result.error_message or ""):
                self.logger.warning(f"批量命令 {i+1} 执行失败，继续执行下一个命令")
        
        return results
    
    def _create_error_result(self, error_message: str) -> ExecutionResult:
        """创建错误结果"""
        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=error_message,
            execution_time=0.0,
            container_info=None,
            error_message=error_message
        )
    
    def _create_validation_error_result(self, validation_result: ValidationResult) -> ExecutionResult:
        """创建验证错误结果"""
        error_message = f"验证失败: {'; '.join(validation_result.errors)}"
        if validation_result.warnings:
            error_message += f"; 警告: {'; '.join(validation_result.warnings)}"
        
        return ExecutionResult(
            success=False,
            exit_code=-2,  # 特殊退出码表示验证失败
            stdout="",
            stderr=error_message,
            execution_time=0.0,
            container_info=None,
            error_message=error_message
        )
    
    def _monitor_loop(self):
        """监控循环"""
        while not self._shutdown:
            try:
                # 检查超时
                timeout_executions = self.execution_monitor.check_timeouts()
                for execution_id in timeout_executions:
                    self.logger.warning(f"执行超时: {execution_id}")
                    # 这里可以添加超时处理逻辑
                
                # 休眠一段时间
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(30)
    
    def add_before_execution_hook(self, hook: Callable[[ExecutionContext], None]):
        """添加执行前钩子"""
        self.before_execution_hooks.append(hook)
    
    def add_after_execution_hook(self, hook: Callable[[ExecutionContext, ExecutionResult], None]):
        """添加执行后钩子"""
        self.after_execution_hooks.append(hook)
    
    def get_command_history(self, count: int = 10) -> List[ParsedCommand]:
        """获取命令历史"""
        return self.command_history.get_recent(count)
    
    def search_command_history(self, pattern: str) -> List[ParsedCommand]:
        """搜索命令历史"""
        return self.command_history.search(pattern)
    
    def get_execution_metrics(self) -> ExecutionMetrics:
        """获取执行指标"""
        return self.execution_monitor.get_execution_metrics()
    
    def get_active_executions(self) -> List[ExecutionContext]:
        """获取活动执行"""
        return self.execution_monitor.get_active_executions()
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        metrics = self.get_execution_metrics()
        
        return {
            'initialized': self._initialized,
            'docker_healthy': self.docker_manager.is_healthy(),
            'active_executions': len(self.get_active_executions()),
            'total_executions': metrics.total_executions,
            'success_rate': (metrics.successful_executions / max(metrics.total_executions, 1)) * 100,
            'average_execution_time': metrics.average_execution_time,
            'validation_failure_rate': (metrics.validation_failures / max(metrics.total_executions, 1)) * 100
        }
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理执行引擎...")
        
        self._shutdown = True
        
        # 等待活动执行完成（最多等待30秒）
        timeout = 30
        start_time = time.time()
        while self.get_active_executions() and (time.time() - start_time) < timeout:
            self.logger.info(f"等待活动执行完成... 剩余: {len(self.get_active_executions())}")
            time.sleep(1)
        
        # 清理Docker管理器
        if self.docker_manager:
            self.docker_manager.cleanup()
        
        # 清理命令历史
        self.command_history.clear()
        
        self.logger.info("执行引擎清理完成")
    
    def validate_command_only(self, parsed_command: ParsedCommand) -> ValidationResult:
        """仅验证命令，不执行"""
        return self.validator.validate(parsed_command)
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        docker_info = self.docker_manager.get_system_info() if self.docker_manager else {}
        health_status = self.get_health_status()
        
        return {
            'engine_status': health_status,
            'docker_info': docker_info,
            'config': self.config_manager.to_dict()
        }


class ExecutionProfiler:
    """执行性能分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profiles: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def record_execution(self, command: str, execution_time: float):
        """记录执行时间"""
        with self._lock:
            if command not in self.profiles:
                self.profiles[command] = []
            
            self.profiles[command].append(execution_time)
            
            # 保持最近100次记录
            if len(self.profiles[command]) > 100:
                self.profiles[command].pop(0)
    
    def get_average_time(self, command: str) -> Optional[float]:
        """获取平均执行时间"""
        with self._lock:
            times = self.profiles.get(command, [])
            return sum(times) / len(times) if times else None
    
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """获取性能报告"""
        report = {}
        
        with self._lock:
            for command, times in self.profiles.items():
                if times:
                    report[command] = {
                        'count': len(times),
                        'average': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times),
                        'latest': times[-1]
                    }
        
        return report