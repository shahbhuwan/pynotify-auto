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
    parser.add_argument(
        "--fix-conda", action="store_true", help="Manually fix auto-start hook for Conda/Isolated envs."
    )
    
    args = parser.parse_args()

    if args.version:
        from importlib.metadata import version
        try:
            print(f"pynotify-auto version {version('pynotify-auto')}")
        except:
            print("pynotify-auto version 0.2.3")
        return

    if args.fix_conda:
        import site
        # Get the User Site-Packages (always accessible and usually checked by Conda)
        try:
            target_dir = site.getusersitepackages()
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                
            target = os.path.join(target_dir, "pynotify-auto.pth")
            print(f"Installing universal hook to: {target}")
            with open(target, "w") as f:
                f.write('import sys; exec("try:\\n    import pynotify_auto\\n    pynotify_auto.install_hook()\\nexcept:\\n    pass")')
            print("Successfully installed universal hook! It will now work in ALL environments.")
        except Exception as e:
            print(f"Error installing hook: {e}")
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
