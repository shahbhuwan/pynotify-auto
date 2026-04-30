import multiprocessing
import time
import os

def worker(n):
    # This process should NOT trigger pynotify-auto
    time.sleep(2)

if __name__ == "__main__":
    # Threshold should be set via environment variable
    
    print("Main Process: Starting 4 workers...")
    processes = []
    for i in range(4):
        p = multiprocessing.Process(target=worker, args=(i,))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
        
    print("Main Process: All workers done.")
