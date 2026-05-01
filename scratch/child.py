import time
import os

if __name__ == "__main__":
    print("CHILD: Starting 70-second run...")
    # This should stay SILENT for the whole 70 seconds
    time.sleep(70)
    print("CHILD: Done.")
