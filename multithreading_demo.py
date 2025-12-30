import threading
import time


def worker(thread_id, duration):
    print(f"Thread {thread_id} starting")
    time.sleep(duration)
    print(f"Thread {thread_id} finished after {duration}s")


def main():
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i, i * 0.5 + 0.5))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("All threads completed")


if __name__ == "__main__":
    main()
