import sys
import argparse
import os
from pynotify_auto import show_popup, play_sound, get_config, get_threshold

def main():
    parser = argparse.ArgumentParser(
        description="pynotify-auto: Zero-Code automatic notifications for Python scripts."
    )
    parser.add_argument("--test", action="store_true", help="Trigger a test notification.")
    parser.add_argument("--info", action="store_true", help="Show current configuration and hook status.")
    parser.add_argument("--version", action="store_true", help="Show version.")
    parser.add_argument("--enable", "-e", action="store_true", help="Install the zero-code hook for the current environment.")
    
    args = parser.parse_args()

    if args.version:
        from pynotify_auto import __version__
        print(f"pynotify-auto version {__version__}")
        return

    if args.enable:
        import site
        from pynotify_auto import hook_active
        if hook_active:
            print("Hook is already active!")
            return

        try:
            # Try user site first, then system site
            target_dir = site.getusersitepackages()
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                
            target = os.path.join(target_dir, "pynotify-auto.pth")
            print(f"Installing universal hook to: {target}")
            with open(target, "w") as f:
                f.write(
                    'import sys; exec("try:\\n'
                    '    import pynotify_auto\\n'
                    '    pynotify_auto.install_hook()\\n'
                    'except Exception:\\n'
                    '    pass")\n'
                )
            print("Successfully enabled zero-code notifications!")
            print("Try running: python -c 'import time; time.sleep(6)'")
        except Exception as e:
            print(f"Error enabling hook: {e}")
            print("You might need to run this with higher privileges (e.g., sudo or Admin terminal).")
        return

    if args.info:
        from pynotify_auto import hook_active
        mode = get_config("mode", "popup")
        threshold = get_threshold()
        disabled = get_config("disable", "0") == "1"
        
        print("pynotify-auto Configuration:")
        print(f"  Hook Active: {'YES (Zero-Code enabled)' if hook_active else 'NO (Run pynotify-auto --enable)'}")
        print(f"  Mode:        {mode}")
        print(f"  Threshold:   {threshold}s")
        print(f"  Status:      {'Disabled via ENV' if disabled else 'Ready'}")
        return

    if args.test:
        mode = get_config("mode", "popup")
        msg = "Test notification from pynotify-auto!"
        print(f"Triggering test notification (Mode: {mode})...")
        
        if mode == "sound":
            play_sound()
        else:
            show_popup(msg)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
