"""
Docker命令执行工具测试套件
包含所有核心模块的单元测试
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_manager import ConfigManager, DockerConfig, SecurityConfig, LoggingConfig
from command_parser import CommandParser, ParsedCommand, CommandHistory
from parameter_validator import ParameterValidator, ValidationResult, SecurityValidator
from docker_manager import DockerManager, ContainerManager, ImageManager
from execution_engine import ExecutionEngine, ExecutionMonitor, ExecutionMetrics
from main import DockerCommandExecutor


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        self.config_manager = ConfigManager()
    
    def test_docker_config_defaults(self):
        """测试Docker配置默认值"""
        config = self.config_manager.docker_config
        self.assertEqual(config.base_image, "alpine:latest")
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.memory_limit, "256m")
        self.assertEqual(config.cpu_limit, 0.5)
        self.assertTrue(config.auto_remove)
    
    def test_security_config_defaults(self):
        """测试安全配置默认值"""
        config = self.config_manager.security_config
        self.assertIn("ls", config.allowed_commands)
        self.assertIn("rm", config.blocked_commands)
        self.assertFalse(config.allow_network)
        self.assertFalse(config.allow_privileged)
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        self.assertTrue(self.config_manager.validate_config())
        
        # 无效配置
        self.config_manager.docker_config.timeout = -1
        self.assertFalse(self.config_manager.validate_config())
    
    def test_load_from_file(self):
        """测试从文件加载配置"""
        # 创建临时配置文件
        config_data = {
            "docker": {"timeout": 60},
            "security": {"allow_network": True}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            config_manager = ConfigManager(temp_file)
            self.assertEqual(config_manager.docker_config.timeout, 60)
            self.assertTrue(config_manager.security_config.allow_network)
        finally:
            os.unlink(temp_file)
    
    def test_environment_variables(self):
        """测试环境变量获取"""
        env_vars = self.config_manager.get_environment_variables()
        self.assertIsInstance(env_vars, dict)
        # PATH应该被包含在安全变量中
        if 'PATH' in os.environ:
            self.assertIn('PATH', env_vars)


class TestCommandParser(unittest.TestCase):
    """命令解析器测试"""
    
    def setUp(self):
        self.parser = CommandParser()
    
    def test_basic_parsing(self):
        """测试基础命令解析"""
        cmd = self.parser.parse("ls -la")
        self.assertEqual(cmd.command, "ls")
        self.assertEqual(cmd.args, ["-la"])
        self.assertEqual(cmd.raw_input, "ls -la")
    
    def test_complex_parsing(self):
        """测试复杂命令解析"""
        cmd = self.parser.parse('grep "test string" /tmp/file.txt')
        self.assertEqual(cmd.command, "grep")
        self.assertEqual(cmd.args, ["test string", "/tmp/file.txt"])
    
    def test_special_args_parsing(self):
        """测试特殊参数解析"""
        cmd = self.parser.parse("ls --workdir /tmp --timeout 60 --env VAR=value")
        self.assertEqual(cmd.command, "ls")
        self.assertEqual(cmd.working_dir, "/tmp")
        self.assertEqual(cmd.timeout, 60)
        self.assertEqual(cmd.environment, {"VAR": "value"})
    
    def test_unsupported_operators(self):
        """测试不支持的操作符"""
        with self.assertRaises(ValueError):
            self.parser.parse("ls | grep test")
        
        with self.assertRaises(ValueError):
            self.parser.parse("ls && pwd")
        
        with self.assertRaises(ValueError):
            self.parser.parse("ls > output.txt")
    
    def test_empty_command(self):
        """测试空命令"""
        with self.assertRaises(ValueError):
            self.parser.parse("")
        
        with self.assertRaises(ValueError):
            self.parser.parse("   ")
    
    def test_quote_handling(self):
        """测试引号处理"""
        cmd = self.parser.parse('"ls" "-la"')
        self.assertEqual(cmd.command, "ls")
        self.assertEqual(cmd.args, ["-la"])
    
    def test_command_validation(self):
        """测试命令格式验证"""
        self.assertTrue(self.parser.validate_command_format("ls"))
        self.assertTrue(self.parser.validate_command_format("grep"))
        self.assertFalse(self.parser.validate_command_format("ls;rm"))
        self.assertFalse(self.parser.validate_command_format("very_long_command_name_that_exceeds_limit"))
    
    def test_arguments_validation(self):
        """测试参数验证"""
        self.assertTrue(self.parser.validate_arguments(["-la", "/tmp"]))
        self.assertFalse(self.parser.validate_arguments(["$(whoami)"]))
        self.assertFalse(self.parser.validate_arguments(["`rm -rf /`"]))


class TestCommandHistory(unittest.TestCase):
    """命令历史测试"""
    
    def setUp(self):
        self.history = CommandHistory(max_size=5)
    
    def test_add_command(self):
        """测试添加命令"""
        cmd = ParsedCommand("ls", ["-la"], "ls -la")
        self.history.add(cmd)
        self.assertEqual(len(self.history.history), 1)
    
    def test_max_size_limit(self):
        """测试最大大小限制"""
        for i in range(10):
            cmd = ParsedCommand(f"cmd{i}", [], f"cmd{i}")
            self.history.add(cmd)
        
        self.assertEqual(len(self.history.history), 5)
        # 应该保留最新的5个命令
        self.assertEqual(self.history.history[-1].command, "cmd9")
    
    def test_search(self):
        """测试搜索功能"""
        commands = ["ls", "grep", "find", "ls"]
        for cmd in commands:
            self.history.add(ParsedCommand(cmd, [], cmd))
        
        results = self.history.search("ls")
        self.assertEqual(len(results), 2)
    
    def test_get_recent(self):
        """测试获取最近命令"""
        for i in range(3):
            cmd = ParsedCommand(f"cmd{i}", [], f"cmd{i}")
            self.history.add(cmd)
        
        recent = self.history.get_recent(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[-1].command, "cmd2")


class TestParameterValidator(unittest.TestCase):
    """参数验证器测试"""
    
    def setUp(self):
        from config_manager import SecurityConfig
        self.security_config = SecurityConfig()
        self.validator = ParameterValidator(self.security_config)
    
    def test_allowed_command(self):
        """测试允许的命令"""
        cmd = ParsedCommand("ls", ["-la"], "ls -la")
        result = self.validator.validate(cmd)
        self.assertTrue(result.is_valid)
    
    def test_blocked_command(self):
        """测试被禁止的命令"""
        cmd = ParsedCommand("rm", ["-rf", "/"], "rm -rf /")
        result = self.validator.validate(cmd)
        self.assertFalse(result.is_valid)
        self.assertIn("被明确禁止", str(result.errors))
    
    def test_unknown_command(self):
        """测试未知命令"""
        cmd = ParsedCommand("unknown_cmd", [], "unknown_cmd")
        result = self.validator.validate(cmd)
        self.assertFalse(result.is_valid)
        self.assertIn("不在允许列表中", str(result.errors))
    
    def test_dangerous_arguments(self):
        """测试危险参数"""
        cmd = ParsedCommand("ls", ["$(rm -rf /)"], "ls $(rm -rf /)")
        result = self.validator.validate(cmd)
        self.assertFalse(result.is_valid)
    
    def test_path_validation(self):
        """测试路径验证"""
        # 安全路径
        cmd = ParsedCommand("ls", ["/tmp"], "ls /tmp")
        result = self.validator.validate(cmd)
        self.assertTrue(result.is_valid)
        
        # 危险路径
        cmd = ParsedCommand("cat", ["/etc/shadow"], "cat /etc/shadow")
        result = self.validator.validate(cmd)
        self.assertFalse(result.is_valid)
    
    def test_argument_length(self):
        """测试参数长度限制"""
        long_arg = "a" * 2000
        cmd = ParsedCommand("echo", [long_arg], f"echo {long_arg}")
        result = self.validator.validate(cmd)
        self.assertFalse(result.is_valid)
    
    def test_risk_level_assessment(self):
        """测试风险级别评估"""
        # 低风险命令
        cmd = ParsedCommand("pwd", [], "pwd")
        result = self.validator.validate(cmd)
        self.assertEqual(result.risk_level, "low")
        
        # 中等风险命令
        cmd = ParsedCommand("find", ["/", "-name", "*.txt"], "find / -name *.txt")
        result = self.validator.validate(cmd)
        self.assertEqual(result.risk_level, "medium")


class TestExecutionEngine(unittest.TestCase):
    """执行引擎测试"""
    
    def setUp(self):
        # 创建模拟的配置管理器
        self.config_manager = Mock()
        self.config_manager.security_config = SecurityConfig()
        self.config_manager.docker_config = DockerConfig()
        self.config_manager.validate_config.return_value = True
        
        # 创建执行引擎
        with patch('execution_engine.DockerManager'):
            self.engine = ExecutionEngine(self.config_manager)
    
    def test_initialization(self):
        """测试初始化"""
        with patch.object(self.engine.docker_manager, 'initialize', return_value=True):
            self.assertTrue(self.engine.initialize())
            self.assertTrue(self.engine._initialized)
    
    def test_command_validation_only(self):
        """测试仅验证命令"""
        cmd = ParsedCommand("ls", ["-la"], "ls -la")
        result = self.engine.validate_command_only(cmd)
        self.assertIsInstance(result, ValidationResult)
    
    def test_execution_metrics(self):
        """测试执行指标"""
        metrics = self.engine.get_execution_metrics()
        self.assertIsInstance(metrics, ExecutionMetrics)
        self.assertEqual(metrics.total_executions, 0)
    
    @patch('execution_engine.DockerManager')
    def test_execute_with_validation_failure(self, mock_docker_manager):
        """测试验证失败的执行"""
        # 模拟验证失败
        with patch.object(self.engine.validator, 'validate') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["测试错误"],
                warnings=[],
                risk_level="high"
            )
            
            cmd = ParsedCommand("rm", ["-rf", "/"], "rm -rf /")
            result = self.engine.execute(cmd)
            
            self.assertFalse(result.success)
            self.assertIn("验证失败", result.stderr)


class TestDockerCommandExecutor(unittest.TestCase):
    """主应用程序测试"""
    
    def setUp(self):
        with patch('main.ExecutionEngine'):
            self.executor = DockerCommandExecutor()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.executor.config_manager)
        self.assertIsNotNone(self.executor.command_parser)
        self.assertIsNotNone(self.executor.execution_engine)
    
    def test_command_parsing_error(self):
        """测试命令解析错误"""
        with patch.object(self.executor.command_parser, 'parse', side_effect=ValueError("解析错误")):
            result = self.executor.execute_command("invalid command")
            self.assertFalse(result.success)
            self.assertIn("命令解析失败", result.stderr)
    
    def test_validate_command(self):
        """测试命令验证"""
        with patch.object(self.executor.execution_engine, 'validate_command_only') as mock_validate:
            mock_validate.return_value = ValidationResult(True, [], [], "low")
            
            result = self.executor.validate_command("ls -la")
            self.assertTrue(result.is_valid)
    
    def test_get_status(self):
        """测试获取状态"""
        with patch.object(self.executor.execution_engine, 'get_health_status') as mock_health:
            mock_health.return_value = {"initialized": True}
            
            status = self.executor.get_status()
            self.assertIn("health", status)
    
    def test_batch_execution(self):
        """测试批量执行"""
        commands = ["ls", "pwd", "whoami"]
        
        with patch.object(self.executor, 'execute_command') as mock_execute:
            from docker_manager import ExecutionResult
            mock_execute.return_value = ExecutionResult(
                success=True,
                exit_code=0,
                stdout="output",
                stderr="",
                execution_time=0.1,
                container_info=None
            )
            
            results = self.executor.execute_batch(commands)
            self.assertEqual(len(results), 3)
            self.assertEqual(mock_execute.call_count, 3)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_validation(self):
        """端到端验证测试"""
        # 创建完整的配置
        config_manager = ConfigManager()
        
        # 创建命令解析器
        parser = CommandParser()
        
        # 创建验证器
        validator = ParameterValidator(config_manager.security_config)
        
        # 测试完整流程
        cmd = parser.parse("ls -la")
        result = validator.validate(cmd)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(cmd.command, "ls")
        self.assertEqual(cmd.args, ["-la"])
    
    def test_security_chain(self):
        """安全链测试"""
        config_manager = ConfigManager()
        parser = CommandParser()
        validator = ParameterValidator(config_manager.security_config)
        
        # 测试危险命令被阻止
        dangerous_commands = [
            "rm -rf /",
            "sudo su",
            "chmod 777 /etc/passwd",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for dangerous_cmd in dangerous_commands:
            try:
                cmd = parser.parse(dangerous_cmd)
                result = validator.validate(cmd)
                self.assertFalse(result.is_valid, f"危险命令未被阻止: {dangerous_cmd}")
            except ValueError:
                # 解析阶段就被拒绝也是可以的
                pass
    
    def test_safe_commands_allowed(self):
        """安全命令允许测试"""
        config_manager = ConfigManager()
        parser = CommandParser()
        validator = ParameterValidator(config_manager.security_config)
        
        safe_commands = [
            "ls -la",
            "cat /etc/os-release",
            "grep test file.txt",
            "find /tmp -name '*.txt'",
            "head -10 /var/log/messages"
        ]
        
        for safe_cmd in safe_commands:
            cmd = parser.parse(safe_cmd)
            result = validator.validate(cmd)
            self.assertTrue(result.is_valid, f"安全命令被错误阻止: {safe_cmd}")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_classes = [
        TestConfigManager,
        TestCommandParser,
        TestCommandHistory,
        TestParameterValidator,
        TestExecutionEngine,
        TestDockerCommandExecutor,
        TestIntegration
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)