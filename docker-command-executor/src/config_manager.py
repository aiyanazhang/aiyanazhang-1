"""
配置管理模块
处理Docker命令执行工具的配置参数
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging


@dataclass
class DockerConfig:
    """Docker容器配置参数"""
    base_image: str = "alpine:latest"
    timeout: int = 30
    memory_limit: str = "256m"
    cpu_limit: float = 0.5
    network_mode: str = "none"
    auto_remove: bool = True
    read_only: bool = True
    user: str = "1000:1000"  # 非特权用户


@dataclass
class SecurityConfig:
    """安全配置参数"""
    allowed_commands: List[str] = None
    blocked_commands: List[str] = None
    allow_network: bool = False
    allow_privileged: bool = False
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    def __post_init__(self):
        if self.allowed_commands is None:
            self.allowed_commands = [
                "ls", "pwd", "cat", "head", "tail", "whoami", "uname", "date",
                "grep", "awk", "sed", "find", "wc", "sort", "uniq", "echo",
                "basename", "dirname", "realpath", "stat"
            ]
        
        if self.blocked_commands is None:
            self.blocked_commands = [
                "rm", "rmdir", "dd", "mkfs", "fdisk", "mount", "umount",
                "sudo", "su", "passwd", "chown", "chmod", "kill", "killall",
                "reboot", "shutdown", "init", "systemctl", "service"
            ]


@dataclass
class LoggingConfig:
    """日志配置参数"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.docker_config = DockerConfig()
        self.security_config = SecurityConfig()
        self.logging_config = LoggingConfig()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        self._setup_logging()
    
    def load_from_file(self, config_file: str):
        """从配置文件加载配置"""
        import json
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 更新Docker配置
            if 'docker' in config_data:
                docker_data = config_data['docker']
                for key, value in docker_data.items():
                    if hasattr(self.docker_config, key):
                        setattr(self.docker_config, key, value)
            
            # 更新安全配置
            if 'security' in config_data:
                security_data = config_data['security']
                for key, value in security_data.items():
                    if hasattr(self.security_config, key):
                        setattr(self.security_config, key, value)
            
            # 更新日志配置
            if 'logging' in config_data:
                logging_data = config_data['logging']
                for key, value in logging_data.items():
                    if hasattr(self.logging_config, key):
                        setattr(self.logging_config, key, value)
                        
        except Exception as e:
            logging.warning(f"加载配置文件失败: {e}")
    
    def load_from_env(self):
        """从环境变量加载配置"""
        # Docker配置
        self.docker_config.base_image = os.getenv('DOCKER_BASE_IMAGE', self.docker_config.base_image)
        self.docker_config.timeout = int(os.getenv('DOCKER_TIMEOUT', self.docker_config.timeout))
        self.docker_config.memory_limit = os.getenv('DOCKER_MEMORY_LIMIT', self.docker_config.memory_limit)
        self.docker_config.cpu_limit = float(os.getenv('DOCKER_CPU_LIMIT', self.docker_config.cpu_limit))
        self.docker_config.network_mode = os.getenv('DOCKER_NETWORK_MODE', self.docker_config.network_mode)
        
        # 安全配置
        self.security_config.allow_network = os.getenv('SECURITY_ALLOW_NETWORK', 'false').lower() == 'true'
        self.security_config.allow_privileged = os.getenv('SECURITY_ALLOW_PRIVILEGED', 'false').lower() == 'true'
        
        # 日志配置
        self.logging_config.level = os.getenv('LOG_LEVEL', self.logging_config.level)
        self.logging_config.file_path = os.getenv('LOG_FILE', self.logging_config.file_path)
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, self.logging_config.level.upper()),
            format=self.logging_config.format
        )
        
        if self.logging_config.file_path:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.logging_config.file_path,
                maxBytes=self.logging_config.max_size,
                backupCount=self.logging_config.backup_count
            )
            file_handler.setFormatter(logging.Formatter(self.logging_config.format))
            logging.getLogger().addHandler(file_handler)
    
    def validate_config(self) -> bool:
        """验证配置的有效性"""
        try:
            # 验证Docker配置
            if self.docker_config.timeout <= 0:
                raise ValueError("Docker超时时间必须大于0")
            
            if self.docker_config.cpu_limit <= 0 or self.docker_config.cpu_limit > 4.0:
                raise ValueError("CPU限制必须在0到4.0之间")
            
            # 验证安全配置
            if not self.security_config.allowed_commands:
                raise ValueError("必须至少允许一个命令")
            
            # 验证日志配置
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.logging_config.level.upper() not in valid_levels:
                raise ValueError(f"日志级别必须是 {valid_levels} 中的一个")
            
            return True
            
        except Exception as e:
            logging.error(f"配置验证失败: {e}")
            return False
    
    def get_environment_variables(self) -> Dict[str, str]:
        """获取要传递给容器的环境变量"""
        safe_env_vars = [
            'PATH', 'HOME', 'USER', 'TERM', 'LANG', 'LC_ALL',
            'TZ', 'SHELL'
        ]
        
        env_vars = {}
        for var in safe_env_vars:
            if var in os.environ:
                env_vars[var] = os.environ[var]
        
        return env_vars
    
    def to_dict(self) -> Dict:
        """将配置转换为字典格式"""
        return {
            'docker': {
                'base_image': self.docker_config.base_image,
                'timeout': self.docker_config.timeout,
                'memory_limit': self.docker_config.memory_limit,
                'cpu_limit': self.docker_config.cpu_limit,
                'network_mode': self.docker_config.network_mode,
                'auto_remove': self.docker_config.auto_remove,
                'read_only': self.docker_config.read_only,
                'user': self.docker_config.user
            },
            'security': {
                'allowed_commands': self.security_config.allowed_commands,
                'blocked_commands': self.security_config.blocked_commands,
                'allow_network': self.security_config.allow_network,
                'allow_privileged': self.security_config.allow_privileged,
                'max_file_size': self.security_config.max_file_size
            },
            'logging': {
                'level': self.logging_config.level,
                'format': self.logging_config.format,
                'file_path': self.logging_config.file_path,
                'max_size': self.logging_config.max_size,
                'backup_count': self.logging_config.backup_count
            }
        }