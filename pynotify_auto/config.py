
import os
import json

DEFAULT_CONFIG = {
    "remote_backend": None,  # "ntfy" or "telegram"
    "ntfy_topic": None,
    "telegram_bot_token": None,
    "telegram_chat_id": None,
    "progress_interval_minutes": 30,
    "log_lines": 10,
    "threshold": 5.0,
    "mode": "popup",
    "disable": False
}

def load_config():
    config = DEFAULT_CONFIG.copy()
    
    # Check home directory for .pynotify.json
    home = os.path.expanduser("~")
    config_path = os.path.join(home, ".pynotify.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception:
            pass
            
    # Environment variables override config file
    for key in config:
        env_val = os.environ.get(f"PYNOTIFY_{key.upper()}")
        if env_val is not None:
            if isinstance(config[key], bool):
                config[key] = env_val.lower() in ("1", "true", "yes")
            elif isinstance(config[key], int):
                config[key] = int(env_val)
            elif isinstance(config[key], float):
                config[key] = float(env_val)
            else:
                config[key] = env_val
                
    return config
