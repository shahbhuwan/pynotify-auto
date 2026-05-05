import os
import sys
import time

# Set environment variables BEFORE importing pynotify_auto
os.environ["PYNOTIFY_THRESHOLD"] = "5"
os.environ["PYNOTIFY_PROGRESS_INTERVAL"] = "0.1" # 6 second heartbeat

import pynotify_auto
pynotify_auto.install_hook()

print("[Main] Starting deep interception verification...")
print("[Main] This line is a standard Python print().")

# Simulate a deep FD write (like from a C++ extension or GPU kernel)
os.write(1, b"[Deep] This line bypasses sys.stdout and goes directly to FD 1.\n")

print("[Main] Waiting 10 seconds for a heartbeat...")
time.sleep(10)

print("[Main] Test complete. Check your Telegram/Terminal output.")
