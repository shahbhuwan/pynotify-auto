import sys
import argparse
import os
from pynotify_auto import show_popup, play_sound, get_config

def main():
    parser = argparse.ArgumentParser(
        description="pynotify-auto: Zero-Code automatic notifications for Python scripts."
    )
    parser.add_argument("--test", action="store_true", help="Trigger a test notification.")
    parser.add_argument("--info", action="store_true", help="Show current configuration and hook status.")
    parser.add_argument("--version", action="store_true", help="Show version.")
    parser.add_argument("--enable", "-e", action="store_true", help="Install the zero-code hook for the current environment.")
    
    parser.add_argument("--config", action="store_true", help="Interactive setup for remote notifications.")
    
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
                    '    pass")\\n'
                )
            print("Successfully enabled zero-code notifications!")
        except Exception as e:
            print(f"Error enabling hook: {e}")
        return

    if args.info:
        from pynotify_auto import hook_active, get_config
        mode = get_config("mode", "popup")
        threshold = get_config("threshold", 5.0)
        disabled = str(get_config("disable", "0")) == "1"
        backend = get_config("remote_backend")
        
        print("pynotify-auto Configuration:")
        print(f"  Hook Active:     {'YES (Zero-Code enabled)' if hook_active else 'NO (Run pynotify-auto --enable)'}")
        print(f"  Local Mode:      {mode}")
        print(f"  Remote Backend:  {backend if backend else 'None'}")
        if backend == "ntfy":
            print(f"  Ntfy Topic:      {get_config('ntfy_topic')}")
        elif backend == "telegram":
            print(f"  Telegram Bot:    {'Configured' if get_config('telegram_bot_token') else 'Missing Token'}")
            
        print(f"  Threshold:       {threshold}s")
        print(f"  Status:          {'Disabled via config' if disabled else 'Ready'}")
        return

    if args.config:
        import json
        from pynotify_auto import get_config
        home = os.path.expanduser("~")
        config_path = os.path.join(home, ".pynotify.json")
        
        # Load existing config if available
        current = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    current = json.load(f)
            except Exception:
                pass

        print("--- pynotify-auto Remote Setup ---")
        print("This will help you get notifications on your phone.")
        print("-" * 40)
        print("TIP: Press [ENTER] to keep the current value shown in brackets.")
        print("-" * 40 + "\n")
        
        curr_backend = current.get("remote_backend", "none")
        print("1. Choose where to send notifications:")
        print("  1) ntfy (easiest, no account)")
        print("  2) telegram (messaging app)")
        print("  3) none (disable remote alerts)")
        
        choice = input(f"Select option [{curr_backend}]: ").strip().lower()
        
        # Map numbers or keep strings
        mapping = {"1": "ntfy", "2": "telegram", "3": "none"}
        backend = mapping.get(choice, choice) or curr_backend
        
        if backend not in ("ntfy", "telegram"):
            if os.path.exists(config_path):
                os.remove(config_path)
                print("\n✅ Remote notifications disabled.")
            return

        new_config = {"remote_backend": backend}
        
        if backend == "ntfy":
            curr_topic = current.get("ntfy_topic", "my_private_topic")
            topic = input(f"2. Enter your ntfy topic name [{curr_topic}]: ").strip()
            new_config["ntfy_topic"] = topic or curr_topic
            print("   (Make sure you subscribe to this same name in the Ntfy phone app)")
        
        elif backend == "telegram":
            curr_token = current.get("telegram_bot_token", "")
            curr_chat = current.get("telegram_chat_id", "")
            token = input(f"2. Enter your Telegram Bot Token [{curr_token}]: ").strip()
            chat_id = input(f"3. Enter your Telegram Chat ID [{curr_chat}]: ").strip()
            new_config["telegram_bot_token"] = token or curr_token
            new_config["telegram_chat_id"] = chat_id or curr_chat

        curr_interval = current.get("progress_interval_minutes", 30)
        interval = input(f"\n3. Update phone every X minutes while script is running [{curr_interval}]: ").strip()
        new_config["progress_interval_minutes"] = int(interval) if interval else curr_interval

        curr_threshold = current.get("threshold", 5.0)
        threshold = input(f"4. Min. runtime (seconds) to trigger the final 'Finished' alert [{curr_threshold}]: ").strip()
        new_config["threshold"] = float(threshold) if threshold else curr_threshold

        with open(config_path, "w") as f:
            json.dump(new_config, f, indent=4)
        
        print(f"\nConfiguration saved to {config_path}!")
        print("Try it out: pynotify-auto --test")
        return

    if args.test:
        from pynotify_auto import send_remote_notification
        mode = get_config("mode", "popup")
        msg = "Test notification from pynotify-auto!"
        
        # Test remote if configured
        if get_config("remote_backend"):
            print(f"Triggering remote notification via {get_config('remote_backend')}...")
            success = send_remote_notification("This is a test of your remote setup! ✅", title="pynotify-auto Test")
            if not success:
                print("❌ Remote notification FAILED. Check your tokens/topic.")
            else:
                print("✅ Remote notification sent!")

        print(f"Triggering local notification (Mode: {mode})...")
        if mode == "sound":
            play_sound()
        else:
            show_popup(msg)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
