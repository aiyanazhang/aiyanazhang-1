\xef\xbb\xbf import threading
import time

# 创建锁和条件变量用于线程同步
lock = threading.Lock()
condition = threading.Condition(lock)
current_thread = 1  # 1表示线程1执行，6表示线程6执行

def print_hello1(count=10):
    """线程1：打印 hello1"""
    global current_thread
    for i in range(count):
        with condition:
            # 等待直到轮到线程1执行
            while current_thread != 1:
                condition.wait()
            
            # 打印 hello1
            print(f"hello1 (iteration {i+1})")
            time.sleep(0.1)  # 可选：稍微延迟以便观察
            
            # 切换到线程6
            current_thread = 6
            condition.notify_all()

def print_hello6(count=10):
    """线程6：打印 hello6"""
    global current_thread
    for i in range(count):
        with condition:
            # 等待直到轮到线程6执行
            while current_thread != 6:
                condition.wait()
            
            # 打印 hello6
            print(f"hello6 (iteration {i+1})")
            time.sleep(0.1)  # 可选：稍微延迟以便观察
            
            # 切换到线程1
            current_thread = 1
            condition.notify_all()

def main():
    """主函数"""
    print("=" * 50)
    print("多线程交替打印演示")
    print("线程1打印 'hello1'，线程6打印 'hello6'")
    print("=" * 50)
    print()
    
    # 设置打印次数
    iterations = 10
    
    # 创建两个线程
    thread1 = threading.Thread(target=print_hello1, args=(iterations,), name="Thread-1")
    thread6 = threading.Thread(target=print_hello6, args=(iterations,), name="Thread-6")
    
    # 启动线程
    thread1.start()
    thread6.start()
    
    # 等待两个线程完成
    thread1.join()
    thread6.join()
    
    print()
    print("=" * 50)
    print("程序执行完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
