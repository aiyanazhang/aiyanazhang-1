"""
互斥锁演示模块

演示Lock和RLock的使用方式和场景
"""

import threading
import time
import random
from typing import List, Dict, Any


class BankAccount:
    """银行账户类 - 演示锁的基本用法"""
    
    def __init__(self, account_id: str, initial_balance: float = 1000.0):
        self.account_id = account_id
        self.balance = initial_balance
        self.lock = threading.Lock()
        self.transaction_history: List[Dict[str, Any]] = []
        
    def deposit(self, amount: float, description: str = "存款") -> bool:
        """存款操作"""
        if amount <= 0:
            return False
            
        with self.lock:  # 使用with语句自动获取和释放锁
            old_balance = self.balance
            # 模拟处理时间
            time.sleep(0.1)
            self.balance += amount
            
            # 记录交易
            transaction = {
                'type': 'deposit',
                'amount': amount,
                'old_balance': old_balance,
                'new_balance': self.balance,
                'description': description,
                'timestamp': time.time(),
                'thread': threading.current_thread().name
            }
            self.transaction_history.append(transaction)
            
            print(f"[{threading.current_thread().name}] {self.account_id} 存款 {amount:.2f}, "
                  f"余额: {old_balance:.2f} -> {self.balance:.2f}")
            return True
            
    def withdraw(self, amount: float, description: str = "取款") -> bool:
        """取款操作"""
        if amount <= 0:
            return False
            
        with self.lock:
            if self.balance < amount:
                print(f"[{threading.current_thread().name}] {self.account_id} 余额不足，取款失败")
                return False
                
            old_balance = self.balance
            # 模拟处理时间
            time.sleep(0.1)
            self.balance -= amount
            
            # 记录交易
            transaction = {
                'type': 'withdraw',
                'amount': amount,
                'old_balance': old_balance,
                'new_balance': self.balance,
                'description': description,
                'timestamp': time.time(),
                'thread': threading.current_thread().name
            }
            self.transaction_history.append(transaction)
            
            print(f"[{threading.current_thread().name}] {self.account_id} 取款 {amount:.2f}, "
                  f"余额: {old_balance:.2f} -> {self.balance:.2f}")
            return True
            
    def get_balance(self) -> float:
        """获取余额"""
        with self.lock:
            return self.balance
            
    def transfer_to(self, target_account: 'BankAccount', amount: float) -> bool:
        """转账操作 - 演示死锁预防"""
        if amount <= 0:
            return False
            
        # 按账户ID排序获取锁，避免死锁
        first_lock = self.lock if self.account_id < target_account.account_id else target_account.lock
        second_lock = target_account.lock if self.account_id < target_account.account_id else self.lock
        
        with first_lock:
            with second_lock:
                if self.balance < amount:
                    print(f"[{threading.current_thread().name}] 转账失败：{self.account_id} 余额不足")
                    return False
                    
                # 执行转账
                self.balance -= amount
                target_account.balance += amount
                
                print(f"[{threading.current_thread().name}] 转账成功：{self.account_id} -> {target_account.account_id}, "
                      f"金额: {amount:.2f}")
                return True


class Counter:
    """计数器类 - 演示RLock的递归锁定"""
    
    def __init__(self):
        self.value = 0
        self.rlock = threading.RLock()  # 可重入锁
        
    def increment(self) -> None:
        """增加计数"""
        with self.rlock:
            self.value += 1
            print(f"[{threading.current_thread().name}] 计数增加到: {self.value}")
            
    def increment_by(self, amount: int) -> None:
        """按指定数量增加 - 演示递归锁定"""
        with self.rlock:
            print(f"[{threading.current_thread().name}] 开始增加 {amount}")
            for _ in range(amount):
                self.increment()  # 这里会再次获取同一个锁
            print(f"[{threading.current_thread().name}] 增加 {amount} 完成")
            
    def get_value(self) -> int:
        """获取当前值"""
        with self.rlock:
            return self.value


class ResourcePool:
    """资源池 - 演示锁的超时机制"""
    
    def __init__(self, max_resources: int = 3):
        self.max_resources = max_resources
        self.available_resources = list(range(max_resources))
        self.used_resources: Dict[int, str] = {}
        self.lock = threading.Lock()
        
    def acquire_resource(self, timeout: float = 5.0) -> int:
        """获取资源"""
        if self.lock.acquire(timeout=timeout):
            try:
                if not self.available_resources:
                    return -1  # 无可用资源
                    
                resource_id = self.available_resources.pop(0)
                self.used_resources[resource_id] = threading.current_thread().name
                print(f"[{threading.current_thread().name}] 获取资源 {resource_id}")
                return resource_id
            finally:
                self.lock.release()
        else:
            print(f"[{threading.current_thread().name}] 获取资源超时")
            return -1
            
    def release_resource(self, resource_id: int) -> bool:
        """释放资源"""
        with self.lock:
            if resource_id in self.used_resources:
                del self.used_resources[resource_id]
                self.available_resources.append(resource_id)
                print(f"[{threading.current_thread().name}] 释放资源 {resource_id}")
                return True
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """获取资源池状态"""
        with self.lock:
            return {
                'available': len(self.available_resources),
                'used': len(self.used_resources),
                'total': self.max_resources,
                'used_by': self.used_resources.copy()
            }


class LocksDemo:
    """锁演示类"""
    
    def __init__(self):
        self.accounts: List[BankAccount] = []
        self.counter = Counter()
        self.resource_pool = ResourcePool()
        
    def demo_basic_lock(self):
        """演示基础锁使用"""
        print("\n=== 基础锁演示 ===")
        print("演示多线程环境下的账户操作")
        
        # 创建银行账户
        account = BankAccount("ACC001", 1000.0)
        self.accounts = [account]
        
        def random_operations(account: BankAccount, operations_count: int):
            """随机执行账户操作"""
            for _ in range(operations_count):
                operation = random.choice(['deposit', 'withdraw'])
                amount = random.uniform(10, 100)
                
                if operation == 'deposit':
                    account.deposit(amount)
                else:
                    account.withdraw(amount)
                    
                time.sleep(random.uniform(0.1, 0.3))
                
        # 创建多个线程同时操作账户
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=random_operations,
                args=(account, 5),
                name=f"BankTeller{i+1}"
            )
            threads.append(thread)
            
        print(f"创建 {len(threads)} 个银行柜员线程")
        print(f"初始余额: {account.get_balance():.2f}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"最终余额: {account.get_balance():.2f}")
        print(f"交易记录数: {len(account.transaction_history)}")
        
    def demo_reentrant_lock(self):
        """演示可重入锁"""
        print("\n=== 可重入锁演示 ===")
        print("演示RLock的递归锁定特性")
        
        def worker_increment(counter: Counter, batch_size: int):
            """工作线程递增操作"""
            counter.increment_by(batch_size)
            
        # 创建多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=worker_increment,
                args=(self.counter, 3),
                name=f"CounterWorker{i+1}"
            )
            threads.append(thread)
            
        print(f"创建 {len(threads)} 个计数器工作线程")
        print(f"初始计数: {self.counter.get_value()}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"最终计数: {self.counter.get_value()}")
        
    def demo_lock_timeout(self):
        """演示锁超时机制"""
        print("\n=== 锁超时演示 ===")
        print("演示资源池的锁超时机制")
        
        def worker_use_resource(pool: ResourcePool, work_duration: float):
            """工作线程使用资源"""
            resource_id = pool.acquire_resource(timeout=2.0)
            if resource_id != -1:
                try:
                    print(f"[{threading.current_thread().name}] 使用资源 {resource_id}，工作 {work_duration:.1f}秒")
                    time.sleep(work_duration)
                finally:
                    pool.release_resource(resource_id)
            else:
                print(f"[{threading.current_thread().name}] 未能获取资源")
                
        # 创建多个线程竞争有限资源
        threads = []
        work_durations = [1.5, 2.0, 1.0, 3.0, 0.5]  # 不同的工作时长
        
        for i, duration in enumerate(work_durations):
            thread = threading.Thread(
                target=worker_use_resource,
                args=(self.resource_pool, duration),
                name=f"ResourceWorker{i+1}"
            )
            threads.append(thread)
            
        print(f"创建 {len(threads)} 个资源使用线程")
        print(f"资源池状态: {self.resource_pool.get_status()}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            time.sleep(0.2)  # 错开启动时间
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"最终资源池状态: {self.resource_pool.get_status()}")
        
    def demo_deadlock_prevention(self):
        """演示死锁预防"""
        print("\n=== 死锁预防演示 ===")
        print("演示通过锁排序避免死锁")
        
        # 创建两个账户
        account1 = BankAccount("ACC001", 1000.0)
        account2 = BankAccount("ACC002", 1500.0)
        
        def transfer_worker(from_acc: BankAccount, to_acc: BankAccount, amount: float):
            """转账工作线程"""
            time.sleep(random.uniform(0.1, 0.5))  # 随机延迟
            from_acc.transfer_to(to_acc, amount)
            
        # 创建相互转账的线程（可能导致死锁）
        threads = []
        
        # 线程1: ACC001 -> ACC002
        thread1 = threading.Thread(
            target=transfer_worker,
            args=(account1, account2, 100.0),
            name="Transfer1to2"
        )
        
        # 线程2: ACC002 -> ACC001
        thread2 = threading.Thread(
            target=transfer_worker,
            args=(account2, account1, 150.0),
            name="Transfer2to1"
        )
        
        threads.extend([thread1, thread2])
        
        print("创建相互转账线程（使用锁排序避免死锁）")
        print(f"ACC001 初始余额: {account1.get_balance():.2f}")
        print(f"ACC002 初始余额: {account2.get_balance():.2f}")
        
        # 启动线程
        for thread in threads:
            thread.start()
            
        # 等待完成
        for thread in threads:
            thread.join()
            
        print(f"ACC001 最终余额: {account1.get_balance():.2f}")
        print(f"ACC002 最终余额: {account2.get_balance():.2f}")
        print("死锁预防成功")
        
    def run_all_demos(self):
        """运行所有锁演示"""
        print("开始互斥锁演示...")
        
        try:
            self.demo_basic_lock()
            time.sleep(1)
            
            self.demo_reentrant_lock()
            time.sleep(1)
            
            self.demo_lock_timeout()
            time.sleep(1)
            
            self.demo_deadlock_prevention()
            
        except KeyboardInterrupt:
            print("\n锁演示被用户中断")
        except Exception as e:
            print(f"\n锁演示过程中发生错误: {e}")
        finally:
            print("\n互斥锁演示结束")


def main():
    """主函数"""
    demo = LocksDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()