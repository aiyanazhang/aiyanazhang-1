#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件
对文件清理工具进行单元测试和集成测试
"""

import unittest
import tempfile
import shutil
import os
import time
from pathlib import Path

# 导入要测试的模块
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config_manager import ConfigManager
from input_validator import InputValidator, RiskLevel
from file_matcher import FileMatchEngine
from safety_checker import SafetyChecker
from backup_manager import BackupManager
from file_deleter import FileDeleter


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test.conf")
        
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config(self):
        """测试默认配置"""
        config = ConfigManager()
        
        # 测试基本配置项
        self.assertIsNotNone(config.get('DEFAULT_BACKUP_DIR'))
        self.assertEqual(config.get_int('MAX_BACKUP_AGE_DAYS'), 30)
        self.assertEqual(config.get_bool('ENABLE_BACKUP'), True)
    
    def test_protected_dirs(self):
        """测试保护目录"""
        config = ConfigManager()
        
        protected_dirs = config.get_protected_dirs()
        self.assertIn('/bin', protected_dirs)
        self.assertIn('/usr', protected_dirs)
        self.assertIn('/etc', protected_dirs)
    
    def test_is_protected_dir(self):
        """测试保护目录检查"""
        config = ConfigManager()
        
        self.assertTrue(config.is_protected_dir('/bin/bash'))
        self.assertTrue(config.is_protected_dir('/usr/local/bin/python'))
        self.assertFalse(config.is_protected_dir('/home/user/test.txt'))


class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""
    
    def setUp(self):
        """测试设置"""
        self.validator = InputValidator()
    
    def test_empty_input(self):
        """测试空输入"""
        result = self.validator.validate_input("")
        self.assertFalse(result.is_valid)
        self.assertIn("不能为空", result.message)
    
    def test_dangerous_patterns(self):
        """测试危险模式"""
        dangerous_patterns = ['*', '/*', '~/*']
        
        for pattern in dangerous_patterns:
            result = self.validator.validate_input(pattern)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.risk_level, RiskLevel.EXTREME)
    
    def test_safe_patterns(self):
        """测试安全模式"""
        safe_patterns = ['*.tmp', '*.log', 'temp*', 'specific_file.txt']
        
        for pattern in safe_patterns:
            result = self.validator.validate_input(pattern)
            self.assertTrue(result.is_valid)
            self.assertIn(result.risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM])
    
    def test_system_patterns(self):
        """测试系统文件模式"""
        system_patterns = ['/bin/bash', '/etc/passwd', '/usr/bin/python']
        
        for pattern in system_patterns:
            result = self.validator.validate_input(pattern)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.risk_level, RiskLevel.EXTREME)


class TestFileMatchEngine(unittest.TestCase):
    """文件匹配引擎测试"""
    
    def setUp(self):
        """测试设置"""
        self.test_dir = tempfile.mkdtemp()
        self.engine = FileMatchEngine(self.test_dir)
        
        # 创建测试文件
        self.test_files = [
            'test1.txt',
            'test2.log', 
            'backup.bak',
            'temp_file.tmp',
            'config.json'
        ]
        
        for filename in self.test_files:
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content for {filename}")
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_exact_match(self):
        """测试精确匹配"""
        result = self.engine.find_files('test1.txt')
        
        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.files[0].name, 'test1.txt')
    
    def test_wildcard_match(self):
        """测试通配符匹配"""
        result = self.engine.find_files('*.txt')
        
        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.files[0].name, 'test1.txt')
    
    def test_extension_match(self):
        """测试扩展名匹配"""
        result = self.engine.find_files('*.log')
        
        self.assertEqual(result.total_count, 1)
        self.assertEqual(result.files[0].name, 'test2.log')
    
    def test_prefix_match(self):
        """测试前缀匹配"""
        result = self.engine.find_files('test*')
        
        self.assertEqual(result.total_count, 2)
        file_names = [f.name for f in result.files]
        self.assertIn('test1.txt', file_names)
        self.assertIn('test2.log', file_names)
    
    def test_no_match(self):
        """测试无匹配"""
        result = self.engine.find_files('nonexistent.xyz')
        
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.files), 0)


class TestSafetyChecker(unittest.TestCase):
    """安全检查器测试"""
    
    def setUp(self):
        """测试设置"""
        self.checker = SafetyChecker()
        self.test_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.safe_file = os.path.join(self.test_dir, 'temp.tmp')
        self.config_file = os.path.join(self.test_dir, '.bashrc')
        self.large_file = os.path.join(self.test_dir, 'large.dat')
        
        # 创建文件
        with open(self.safe_file, 'w') as f:
            f.write("temporary content")
        
        with open(self.config_file, 'w') as f:
            f.write("# bash configuration")
        
        # 创建大文件 (>100MB for testing)
        with open(self.large_file, 'wb') as f:
            f.write(b'0' * (101 * 1024 * 1024))
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_safe_file(self):
        """测试安全文件检查"""
        from file_matcher import FileInfo
        
        stat = os.stat(self.safe_file)
        file_info = FileInfo(
            path=self.safe_file,
            name='temp.tmp',
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_hidden=False,
            is_dir=False,
            extension='tmp',
            relative_path='temp.tmp'
        )
        
        risk = self.checker.check_file_safety(file_info)
        
        # 临时文件应该被标记为安全
        self.assertTrue(risk.can_delete)
        # 应该有安全扩展名的检查
        safe_checks = [c for c in risk.checks if 'tmp' in c.reason and 'safe' in c.reason.lower()]
        self.assertTrue(len(safe_checks) > 0)
    
    def test_config_file(self):
        """测试配置文件检查"""
        from file_matcher import FileInfo
        
        stat = os.stat(self.config_file)
        file_info = FileInfo(
            path=self.config_file,
            name='.bashrc',
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_hidden=True,
            is_dir=False,
            extension='',
            relative_path='.bashrc'
        )
        
        risk = self.checker.check_file_safety(file_info)
        
        # 配置文件应该有更高的风险等级
        self.assertTrue(risk.can_delete)  # 虽然可以删除但需要确认
        self.assertGreater(risk.risk_score, 20)  # 应该有一定的风险分数
    
    def test_large_file(self):
        """测试大文件检查"""
        from file_matcher import FileInfo
        
        stat = os.stat(self.large_file)
        file_info = FileInfo(
            path=self.large_file,
            name='large.dat',
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_hidden=False,
            is_dir=False,
            extension='dat',
            relative_path='large.dat'
        )
        
        risk = self.checker.check_file_safety(file_info)
        
        # 大文件应该有警告
        large_file_checks = [c for c in risk.checks if '大文件' in c.reason]
        self.assertTrue(len(large_file_checks) > 0)


class TestBackupManager(unittest.TestCase):
    """备份管理器测试"""
    
    def setUp(self):
        """测试设置"""
        self.test_dir = tempfile.mkdtemp()
        
        # 使用临时目录作为备份目录
        import os
        os.environ['HOME'] = self.test_dir
        
        self.backup_manager = BackupManager()
        
        # 创建测试文件
        self.test_files_dir = os.path.join(self.test_dir, 'test_files')
        os.makedirs(self.test_files_dir)
        
        self.test_file1 = os.path.join(self.test_files_dir, 'file1.txt')
        self.test_file2 = os.path.join(self.test_files_dir, 'file2.log')
        
        with open(self.test_file1, 'w') as f:
            f.write("Test file 1 content")
        
        with open(self.test_file2, 'w') as f:
            f.write("Test file 2 content")
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_create_backup(self):
        """测试创建备份"""
        from file_matcher import FileInfo
        
        # 创建文件信息
        files = []
        for file_path in [self.test_file1, self.test_file2]:
            stat = os.stat(file_path)
            file_info = FileInfo(
                path=file_path,
                name=os.path.basename(file_path),
                size=stat.st_size,
                modified_time=stat.st_mtime,
                is_hidden=False,
                is_dir=False,
                extension=os.path.splitext(file_path)[1][1:],
                relative_path=os.path.basename(file_path)
            )
            files.append(file_info)
        
        # 创建备份
        backup_id = self.backup_manager.create_backup(files, "测试备份")
        
        self.assertIsNotNone(backup_id)
        self.assertTrue(backup_id.startswith('backup_'))
        
        # 检查备份是否存在
        backup_info = self.backup_manager.get_backup_info(backup_id)
        self.assertIsNotNone(backup_info)
        self.assertEqual(backup_info.file_count, 2)
        self.assertEqual(backup_info.description, "测试备份")
    
    def test_list_backups(self):
        """测试列出备份"""
        # 先创建一个备份
        from file_matcher import FileInfo
        
        stat = os.stat(self.test_file1)
        file_info = FileInfo(
            path=self.test_file1,
            name=os.path.basename(self.test_file1),
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_hidden=False,
            is_dir=False,
            extension='txt',
            relative_path=os.path.basename(self.test_file1)
        )
        
        backup_id = self.backup_manager.create_backup([file_info], "测试备份")
        
        # 列出备份
        backups = self.backup_manager.list_backups()
        
        self.assertGreater(len(backups), 0)
        self.assertEqual(backups[0].backup_id, backup_id)


class TestFileDeleter(unittest.TestCase):
    """文件删除器测试"""
    
    def setUp(self):
        """测试设置"""
        self.test_dir = tempfile.mkdtemp()
        self.deleter = FileDeleter(enable_backup=False, dry_run=True)  # 测试模式
        
        # 创建测试文件
        self.test_file = os.path.join(self.test_dir, 'test_delete.txt')
        with open(self.test_file, 'w') as f:
            f.write("Test content for deletion")
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_dry_run_delete(self):
        """测试模拟删除"""
        from file_matcher import FileInfo
        
        stat = os.stat(self.test_file)
        file_info = FileInfo(
            path=self.test_file,
            name='test_delete.txt',
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_hidden=False,
            is_dir=False,
            extension='txt',
            relative_path='test_delete.txt'
        )
        
        result = self.deleter.delete_files([file_info], "测试删除")
        
        # 模拟模式下文件应该被跳过
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(len(result.successful), 0)
        self.assertEqual(len(result.failed), 0)
        
        # 文件应该仍然存在
        self.assertTrue(os.path.exists(self.test_file))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试设置"""
        self.test_dir = tempfile.mkdtemp()
        
        # 创建测试文件结构
        self.create_test_files()
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_files(self):
        """创建测试文件结构"""
        files = [
            'temp1.tmp',
            'temp2.tmp', 
            'log1.log',
            'important.txt',
            'backup.bak',
            '.hidden_config'
        ]
        
        for filename in files:
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Content of {filename}")
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 1. 搜索文件
        engine = FileMatchEngine(self.test_dir)
        result = engine.find_files('*.tmp')
        
        self.assertEqual(result.total_count, 2)
        
        # 2. 安全检查
        checker = SafetyChecker()
        file_risks = checker.check_files_batch(result.files)
        
        self.assertEqual(len(file_risks), 2)
        
        # 3. 检查所有临时文件都是可删除的
        for risk in file_risks:
            self.assertTrue(risk.can_delete)
        
        # 4. 模拟删除
        deleter = FileDeleter(enable_backup=False, dry_run=True)
        delete_result = deleter.delete_files(result.files, "集成测试")
        
        self.assertEqual(len(delete_result.skipped), 2)  # 模拟模式下都被跳过
        self.assertEqual(len(delete_result.successful), 0)
        self.assertEqual(len(delete_result.failed), 0)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestConfigManager,
        TestInputValidator,
        TestFileMatchEngine,
        TestSafetyChecker,
        TestBackupManager,
        TestFileDeleter,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 显示测试结果统计
    print(f"\n{'='*60}")
    print(f"测试结果统计:")
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)