
import time
import sys

print("🚀 Starting 8-minute stress test...")
for minute in range(1, 9):
    print(f"\n--- Minute {minute} of 8 ---")
    for sec in range(1, 61):
        # Print a milestone every 10 seconds
        if sec % 10 == 0:
            print(f"[Minute {minute}] Milestone: {sec} seconds passed...")
        
        # Every 30 seconds, dump a bunch of logs to test the 10-line limit
        if sec == 30:
            for j in range(20):
                print(f"Boring background log {j}...")
                
        time.sleep(1)

print("✅ Stress test complete!")
