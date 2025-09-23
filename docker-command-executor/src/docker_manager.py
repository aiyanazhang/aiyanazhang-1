"""
Docker管理器模块
管理Docker容器的生命周期，包括创建、配置、启动、监控和清理
"""

import docker
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from .config_manager import DockerConfig, SecurityConfig
from .command_parser import ParsedCommand


@dataclass
class ContainerInfo:
    """容器信息"""
    container_id: str
    name: str
    status: str
    created_at: float
    command: str
    working_dir: Optional[str] = None
    environment: Dict[str, str] = None
    resource_usage: Dict[str, Any] = None


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    container_info: ContainerInfo
    error_message: Optional[str] = None


class DockerClientManager:
    """Docker客户端管理器"""
    
    def __init__(self):
        self.client: Optional[docker.DockerClient] = None
        self.logger = logging.getLogger(__name__)
        self._connect_lock = threading.Lock()
    
    def connect(self) -> bool:
        """连接到Docker守护进程"""
        with self._connect_lock:
            try:
                self.client = docker.from_env()
                # 测试连接
                self.client.ping()
                self.logger.info("成功连接到Docker守护进程")
                return True
            except docker.errors.DockerException as e:
                self.logger.error(f"连接Docker失败: {e}")
                self.client = None
                return False
            except Exception as e:
                self.logger.error(f"未知错误: {e}")
                self.client = None
                return False
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        if self.client is None:
            return False
        
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            try:
                self.client.close()
                self.logger.info("已断开Docker连接")
            except Exception as e:
                self.logger.warning(f"断开Docker连接时出错: {e}")
            finally:
                self.client = None


class ImageManager:
    """镜像管理器"""
    
    def __init__(self, client: docker.DockerClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self._pull_lock = threading.Lock()
    
    def ensure_image(self, image_name: str) -> bool:
        """确保镜像存在，如果不存在则拉取"""
        try:
            # 检查本地是否有镜像
            self.client.images.get(image_name)
            self.logger.debug(f"镜像 {image_name} 已存在")
            return True
        except docker.errors.ImageNotFound:
            self.logger.info(f"镜像 {image_name} 不存在，开始拉取...")
            return self._pull_image(image_name)
    
    def _pull_image(self, image_name: str) -> bool:
        """拉取镜像"""
        with self._pull_lock:
            try:
                # 再次检查镜像是否存在（可能其他线程已经拉取）
                try:
                    self.client.images.get(image_name)
                    return True
                except docker.errors.ImageNotFound:
                    pass
                
                self.logger.info(f"开始拉取镜像: {image_name}")
                self.client.images.pull(image_name)
                self.logger.info(f"成功拉取镜像: {image_name}")
                return True
                
            except docker.errors.APIError as e:
                self.logger.error(f"拉取镜像失败: {e}")
                return False
            except Exception as e:
                self.logger.error(f"拉取镜像时发生未知错误: {e}")
                return False
    
    def list_images(self) -> List[str]:
        """列出本地镜像"""
        try:
            images = self.client.images.list()
            return [tag for image in images for tag in image.tags if tag]
        except Exception as e:
            self.logger.error(f"列出镜像失败: {e}")
            return []
    
    def remove_image(self, image_name: str) -> bool:
        """删除镜像"""
        try:
            self.client.images.remove(image_name, force=True)
            self.logger.info(f"已删除镜像: {image_name}")
            return True
        except Exception as e:
            self.logger.error(f"删除镜像失败: {e}")
            return False


class ContainerManager:
    """容器管理器"""
    
    def __init__(self, client: docker.DockerClient, docker_config: DockerConfig, security_config: SecurityConfig):
        self.client = client
        self.docker_config = docker_config
        self.security_config = security_config
        self.logger = logging.getLogger(__name__)
        self.active_containers: Dict[str, docker.models.containers.Container] = {}
        self._container_lock = threading.Lock()
    
    def create_container(self, parsed_command: ParsedCommand, mount_path: Optional[str] = None) -> Optional[str]:
        """创建容器"""
        try:
            # 生成容器名称
            container_name = f"cmd-executor-{int(time.time() * 1000)}"
            
            # 构建完整命令
            full_command = [parsed_command.command] + parsed_command.args
            
            # 配置容器参数
            container_config = self._build_container_config(
                parsed_command, container_name, full_command, mount_path
            )
            
            # 创建容器
            self.logger.info(f"创建容器: {container_name}")
            container = self.client.containers.create(**container_config)
            
            # 记录容器
            with self._container_lock:
                self.active_containers[container.id] = container
            
            self.logger.info(f"容器创建成功: {container_name} (ID: {container.short_id})")
            return container.id
            
        except docker.errors.APIError as e:
            self.logger.error(f"创建容器失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"创建容器时发生未知错误: {e}")
            return None
    
    def _build_container_config(self, parsed_command: ParsedCommand, container_name: str, 
                              full_command: List[str], mount_path: Optional[str]) -> Dict[str, Any]:
        """构建容器配置"""
        config = {
            'image': self.docker_config.base_image,
            'command': full_command,
            'name': container_name,
            'detach': True,
            'auto_remove': self.docker_config.auto_remove,
            'read_only': self.docker_config.read_only,
            'network_mode': self.docker_config.network_mode,
            'user': self.docker_config.user,
            'mem_limit': self.docker_config.memory_limit,
            'cpu_quota': int(self.docker_config.cpu_limit * 100000),
            'cpu_period': 100000,
            'security_opt': ['no-new-privileges:true'],
            'cap_drop': ['ALL'],
            'cap_add': ['CHOWN', 'DAC_OVERRIDE', 'FOWNER', 'SETGID', 'SETUID'],
        }
        
        # 设置工作目录
        if parsed_command.working_dir:
            config['working_dir'] = parsed_command.working_dir
        elif mount_path:
            config['working_dir'] = '/workspace'
        
        # 设置环境变量
        if parsed_command.environment:
            config['environment'] = parsed_command.environment
        
        # 设置挂载点
        if mount_path:
            config['volumes'] = {mount_path: {'bind': '/workspace', 'mode': 'ro'}}
        
        # 禁用网络（如果配置要求）
        if not self.security_config.allow_network:
            config['network_disabled'] = True
        
        # 设置资源限制
        config['ulimits'] = [
            docker.types.Ulimit(name='nofile', soft=1024, hard=1024),
            docker.types.Ulimit(name='nproc', soft=50, hard=50),
        ]
        
        # 设置只读挂载的tmpfs
        config['tmpfs'] = {
            '/tmp': 'size=100m,noexec,nosuid,nodev',
            '/var/tmp': 'size=50m,noexec,nosuid,nodev'
        }
        
        return config
    
    def start_container(self, container_id: str) -> bool:
        """启动容器"""
        try:
            container = self.active_containers.get(container_id)
            if not container:
                self.logger.error(f"容器不存在: {container_id}")
                return False
            
            container.start()
            self.logger.info(f"容器启动成功: {container.short_id}")
            return True
            
        except docker.errors.APIError as e:
            self.logger.error(f"启动容器失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"启动容器时发生未知错误: {e}")
            return False
    
    def wait_for_container(self, container_id: str, timeout: Optional[int] = None) -> ExecutionResult:
        """等待容器执行完成"""
        container = self.active_containers.get(container_id)
        if not container:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="容器不存在",
                execution_time=0,
                container_info=None,
                error_message="容器不存在"
            )
        
        start_time = time.time()
        
        try:
            # 等待容器完成
            if timeout is None:
                timeout = self.docker_config.timeout
            
            result = container.wait(timeout=timeout)
            execution_time = time.time() - start_time
            
            # 获取输出
            stdout = ""
            stderr = ""
            
            try:
                logs = container.logs(stdout=True, stderr=True, stream=False)
                if isinstance(logs, bytes):
                    stdout = logs.decode('utf-8', errors='replace')
                else:
                    # 分离stdout和stderr
                    stdout_logs = container.logs(stdout=True, stderr=False)
                    stderr_logs = container.logs(stdout=False, stderr=True)
                    stdout = stdout_logs.decode('utf-8', errors='replace') if stdout_logs else ""
                    stderr = stderr_logs.decode('utf-8', errors='replace') if stderr_logs else ""
            except Exception as e:
                self.logger.warning(f"获取容器日志失败: {e}")
                stderr = f"获取日志失败: {e}"
            
            # 构建容器信息
            container_info = ContainerInfo(
                container_id=container.id,
                name=container.name,
                status=container.status,
                created_at=start_time,
                command=str(container.attrs.get('Config', {}).get('Cmd', [])),
                working_dir=container.attrs.get('Config', {}).get('WorkingDir'),
                environment=container.attrs.get('Config', {}).get('Env', [])
            )
            
            exit_code = result['StatusCode']
            success = exit_code == 0
            
            return ExecutionResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                container_info=container_info
            )
            
        except docker.errors.APIError as e:
            execution_time = time.time() - start_time
            error_msg = f"Docker API错误: {e}"
            self.logger.error(error_msg)
            
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=error_msg,
                execution_time=execution_time,
                container_info=None,
                error_message=error_msg
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"执行失败: {e}"
            self.logger.error(error_msg)
            
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=error_msg,
                execution_time=execution_time,
                container_info=None,
                error_message=error_msg
            )
    
    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """停止容器"""
        try:
            container = self.active_containers.get(container_id)
            if not container:
                return True  # 容器不存在，认为已停止
            
            container.stop(timeout=timeout)
            self.logger.info(f"容器已停止: {container.short_id}")
            return True
            
        except docker.errors.NotFound:
            # 容器已经不存在
            return True
        except Exception as e:
            self.logger.error(f"停止容器失败: {e}")
            return False
    
    def remove_container(self, container_id: str) -> bool:
        """删除容器"""
        try:
            with self._container_lock:
                container = self.active_containers.pop(container_id, None)
            
            if container:
                try:
                    container.remove(force=True)
                    self.logger.info(f"容器已删除: {container.short_id}")
                except docker.errors.NotFound:
                    # 容器已经不存在
                    pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"删除容器失败: {e}")
            return False
    
    def cleanup_all_containers(self):
        """清理所有活动容器"""
        self.logger.info("开始清理所有容器...")
        
        with self._container_lock:
            container_ids = list(self.active_containers.keys())
        
        for container_id in container_ids:
            try:
                self.stop_container(container_id)
                self.remove_container(container_id)
            except Exception as e:
                self.logger.error(f"清理容器失败 {container_id}: {e}")
        
        self.logger.info("容器清理完成")
    
    def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """获取容器资源使用统计"""
        try:
            container = self.active_containers.get(container_id)
            if not container:
                return None
            
            stats = container.stats(stream=False)
            return stats
            
        except Exception as e:
            self.logger.error(f"获取容器统计失败: {e}")
            return None


class DockerManager:
    """Docker管理器主类"""
    
    def __init__(self, docker_config: DockerConfig, security_config: SecurityConfig):
        self.docker_config = docker_config
        self.security_config = security_config
        self.logger = logging.getLogger(__name__)
        
        self.client_manager = DockerClientManager()
        self.image_manager: Optional[ImageManager] = None
        self.container_manager: Optional[ContainerManager] = None
        
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化Docker管理器"""
        if self._initialized:
            return True
        
        # 连接Docker客户端
        if not self.client_manager.connect():
            return False
        
        # 初始化管理器
        self.image_manager = ImageManager(self.client_manager.client)
        self.container_manager = ContainerManager(
            self.client_manager.client, 
            self.docker_config, 
            self.security_config
        )
        
        # 确保基础镜像存在
        if not self.image_manager.ensure_image(self.docker_config.base_image):
            self.logger.error(f"无法获取基础镜像: {self.docker_config.base_image}")
            return False
        
        self._initialized = True
        self.logger.info("Docker管理器初始化完成")
        return True
    
    def execute_command(self, parsed_command: ParsedCommand, mount_path: Optional[str] = None) -> ExecutionResult:
        """执行命令"""
        if not self._initialized:
            if not self.initialize():
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="Docker管理器初始化失败",
                    execution_time=0,
                    container_info=None,
                    error_message="Docker管理器初始化失败"
                )
        
        container_id = None
        try:
            # 创建容器
            container_id = self.container_manager.create_container(parsed_command, mount_path)
            if not container_id:
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="创建容器失败",
                    execution_time=0,
                    container_info=None,
                    error_message="创建容器失败"
                )
            
            # 启动容器
            if not self.container_manager.start_container(container_id):
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="启动容器失败",
                    execution_time=0,
                    container_info=None,
                    error_message="启动容器失败"
                )
            
            # 等待执行完成
            timeout = parsed_command.timeout or self.docker_config.timeout
            result = self.container_manager.wait_for_container(container_id, timeout)
            
            return result
            
        finally:
            # 清理容器
            if container_id:
                self.container_manager.remove_container(container_id)
    
    def cleanup(self):
        """清理资源"""
        if self.container_manager:
            self.container_manager.cleanup_all_containers()
        
        if self.client_manager:
            self.client_manager.disconnect()
        
        self._initialized = False
        self.logger.info("Docker管理器已清理")
    
    def is_healthy(self) -> bool:
        """检查Docker服务健康状态"""
        return self.client_manager.is_connected()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取Docker系统信息"""
        if not self.client_manager.client:
            return {}
        
        try:
            return self.client_manager.client.info()
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}
