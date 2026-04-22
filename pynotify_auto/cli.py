import sys
import argparse
import os
from pynotify_auto import _show_popup, _play_sound, _get_config, _get_threshold

def main():
    parser = argparse.ArgumentParser(
        description="pynotify-auto: Zero-Code automatic notifications for Python scripts."
    )
    parser.add_argument(
        "--test", action="store_true", help="Trigger a test notification to verify settings."
    )
    parser.add_argument(
        "--info", action="store_true", help="Show current configuration settings."
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version of pynotify-auto."
    )
    
    args = parser.parse_args()

    if args.version:
        print("pynotify-auto version 0.1.0")
        return

    if args.info:
        mode = _get_config("mode", "popup")
        threshold = _get_threshold()
        disabled = _get_config("disable", "0") == "1"
        
        print("pynotify-auto Configuration:")
        print(f"  Mode:      {mode}")
        print(f"  Threshold: {threshold}s")
        print(f"  Status:    {'Disabled' if disabled else 'Active'}")
        return

    if args.test:
        mode = _get_config("mode", "popup")
        msg = "Test notification from pynotify-auto!"
        print(f"Triggering test notification (Mode: {mode})...")
        
        if mode == "sound":
            _play_sound()
        else:
            _show_popup(msg)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
