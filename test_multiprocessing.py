import time
from multiprocessing import Pool
import os

def work(n):
    print(f"Worker {n} (PID: {os.getpid()}) starting...")
    time.sleep(2)
    return n * n

if __name__ == "__main__":
    print(f"Main Process (PID: {os.getpid()}) starting...")
    # This script will run for 2+ seconds total
    with Pool(4) as p:
        results = p.map(work, range(4))
    print("Main Process finished.")
    time.sleep(6) # Ensure we cross the 5s threshold for the main process
