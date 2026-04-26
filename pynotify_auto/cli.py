import sys
import argparse
import os
from pynotify_auto import show_popup, play_sound, get_config, get_threshold

def main():
    parser = argparse.ArgumentParser(
        description="pynotify-auto: Zero-Code automatic notifications for Python scripts."
    )
    parser.add_argument("--test", action="store_true", help="Trigger a test notification.")
    parser.add_argument("--info", action="store_true", help="Show current configuration.")
    parser.add_argument("--version", action="store_true", help="Show version.")
    parser.add_argument("--fix-conda", action="store_true", help="Fix hook for Conda/Isolated envs.")
    
    args = parser.parse_args()

    if args.version:
        from pynotify_auto import __version__
        print(f"pynotify-auto version {__version__}")
        return

    if args.fix_conda:
        import site
        try:
            target_dir = site.getusersitepackages()
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                
            target = os.path.join(target_dir, "pynotify-auto.pth")
            print(f"Installing universal hook to: {target}")
            # Use importable path instead of hardcoded Windows Lib/site-packages
            with open(target, "w") as f:
                f.write(
                    'import sys; exec("try:\\n'
                    '    import pynotify_auto\\n'
                    '    pynotify_auto.install_hook()\\n'
                    'except Exception:\\n'
                    '    pass")\n'
                )
            print("Successfully installed universal hook!")
        except Exception as e:
            print(f"Error installing hook: {e}")
        return

    if args.info:
        mode = get_config("mode", "popup")
        threshold = get_threshold()
        disabled = get_config("disable", "0") == "1"
        
        print("pynotify-auto Configuration:")
        print(f"  Mode:      {mode}")
        print(f"  Threshold: {threshold}s")
        print(f"  Status:    {'Disabled' if disabled else 'Active'}")
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
