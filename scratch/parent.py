import subprocess
import sys
import os
import time

if __name__ == "__main__":
    print("PARENT: Starting...")
    # Force notification threshold low
    os.environ["PYNOTIFY_THRESHOLD"] = "0.1"
    
    # Run child script
    subprocess.run([sys.executable, "scratch/child.py"])
    
    # Sleep to ensure parent also hits threshold
    time.sleep(1)
    print("PARENT: Done.")
