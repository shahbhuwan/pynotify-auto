import pynotify_auto
import time
import os
import sys
from multiprocessing import Process

def worker(worker_id):
    print(f"[Worker {worker_id}] Starting task in child process (PID {os.getpid()})...")
    time.sleep(10)
    print(f"[Worker {worker_id}] Processing data...")
    time.sleep(10)
    print(f"[Worker {worker_id}] Task completed.")

if __name__ == "__main__":
    # Ensure pynotify-auto is active
    pynotify_auto.install_hook()
    
    # Low threshold for testing
    os.environ["PYNOTIFY_THRESHOLD"] = "2"
    
    print(f"[Main] Starting test with multiprocessing (Parent PID {os.getpid()})")
    
    processes = []
    for i in range(3):
        p = Process(target=worker, args=(i,))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
    print("[Main] All workers finished. Script exiting now.")
