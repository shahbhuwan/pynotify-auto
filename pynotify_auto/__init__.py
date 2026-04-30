"""
pynotify-auto: Zero-code notifications for long-running scripts.

Triggered via .pth file. Calling install_hook() registers an exit handler
to ping the user if the script ran longer than the threshold.
"""

import atexit
import time
import sys
import os
import subprocess
import threading
from collections import deque
from . import config as cfg_module
from . import remote

__version__ = "0.4.3"

_config = cfg_module.load_config()

def get_config(key, default=None):
    """Read config with fallback. Checks environment variables dynamically."""
    env_val = os.environ.get(f"PYNOTIFY_{key.upper()}")
    if env_val is not None:
        return env_val
    return _config.get(key, default)

def get_threshold():
    """Helper to get the current notification threshold. Safely falls back to 5.0."""
    try:
        return float(get_config("threshold", 5.0))
    except (ValueError, TypeError):
        return 5.0


# ---------------------------------------------------------------------------
# Notification back-ends
# ---------------------------------------------------------------------------

def play_sound(success=True):
    """Play a system chime based on exit status."""
    if os.environ.get("GITHUB_ACTIONS"):
        return
    try:
        if sys.platform == "win32":
            import winsound
            tone = winsound.MB_ICONASTERISK if success else winsound.MB_ICONHAND
            winsound.MessageBeep(tone)
        elif sys.platform == "darwin":
            sound = "/System/Library/Sounds/Glass.aiff" if success else "/System/Library/Sounds/Basso.aiff"
            subprocess.run(["afplay", sound], check=False)
        else:
            subprocess.run(["beep"], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def show_popup(msg, success=True):
    """Trigger a native system notification popup."""
    if os.environ.get("GITHUB_ACTIONS"):
        return
    icon = "✅" if success else "❌"
    title = f"{icon} Python Task {'Finished' if success else 'Failed'}"
    try:
        if sys.platform == "win32":
            safe_msg = msg.replace('"', '""')
            ps_script = f"""
            [reflection.assembly]::loadwithpartialname("System.Windows.Forms")
            $notify = new-object system.windows.forms.notifyicon
            $notify.icon = [system.drawing.systemicons]::Information
            $notify.visible = $true
            $notify.showballoontip(5000, "{title}", "{safe_msg}", [system.windows.forms.tooltipicon]::Info)
            start-sleep -s 2
            """
            # Use Popen to make it non-blocking
            subprocess.Popen(
                ["powershell", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif sys.platform == "darwin":
            subprocess.Popen(["osascript", "-e", f'display notification "{msg}" with title "{title}"'])
        else:
            subprocess.Popen(["notify-send", title, msg], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def send_remote_notification(msg, title=None, success=True):
    """Send notification to remote backend (ntfy/telegram)."""
    backend = get_config("remote_backend")
    if not backend:
        return False
    
    if backend == "ntfy":
        topic = get_config("ntfy_topic")
        if topic:
            return remote.send_ntfy(topic, msg, title=title)
    elif backend == "telegram":
        token = get_config("telegram_bot_token")
        chat_id = get_config("telegram_chat_id")
        if token and chat_id:
            # Escape HTML for Telegram
            safe_msg = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if title:
                safe_msg = f"<b>{title}</b>\n\n{safe_msg}"
            return remote.send_telegram(token, chat_id, safe_msg)
    return False

# ---------------------------------------------------------------------------
# Stream Interception
# ---------------------------------------------------------------------------

class StreamInterceptor:
    def __init__(self, original_stream, max_lines=10):
        self.original_stream = original_stream
        self.log_history = deque(maxlen=max_lines)
        self._lock = threading.Lock()

    def write(self, text):
        self.original_stream.write(text)
        if text.strip():
            with self._lock:
                # Add timestamp to each line for context
                timestamp = time.strftime("%H:%M:%S")
                self.log_history.append(f"[{timestamp}] {text.strip()}")

    def flush(self):
        self.original_stream.flush()

    def get_logs(self):
        with self._lock:
            return list(self.log_history)

    def __getattr__(self, name):
        return getattr(self.original_stream, name)

_interceptor = None

def _heartbeat_loop():
    """Background thread that sends periodic updates."""
    global _interceptor
    try:
        interval_mins = get_config("progress_interval_minutes", 30)
        interval = float(interval_mins) * 60
    except (ValueError, TypeError):
        interval = 30 * 60

    if interval <= 0:
        return

    script_name = os.path.basename(sys.argv[0]) if sys.argv else "Python Script"
    print(f"[pynotify-auto] Remote updates active. Next update in {interval/60:.1f} minutes.")
    
    while True:
        time.sleep(interval)
        if not _interceptor:
            continue
            
        logs = _interceptor.get_logs()
        
        if logs:
            log_text = "\n".join(logs)
            msg = f"Still running...\n\nRecent output:\n{log_text}"
            print(f"\n[pynotify-auto] Sending progress update to phone ({get_config('remote_backend')})...")
            success = send_remote_notification(msg, title=f"Progress: {script_name}", success=True)
            if not success:
                 print("[pynotify-auto] ⚠️ Remote update failed (check connection/topic)")


# ---------------------------------------------------------------------------
# Failure tracking
# ---------------------------------------------------------------------------

_exit_code = None

def _detect_failure():
    """True if we're exiting due to a crash or non-zero sys.exit()."""
    global _exit_code

    if _exit_code is not None:
        return _exit_code not in (0, None)

    last_type = getattr(sys, "last_type", None)
    if last_type is not None:
        if last_type is SystemExit:
            last_value = getattr(sys, "last_value", None)
            code = getattr(last_value, "code", None) if last_value else None
            return code not in (None, 0)
        return True 

    return False


def _ping_on_exit():
    """Logic that runs at interpreter shutdown."""
    if get_config("disable") == "1" or get_config("disable") is True:
        return

    elapsed = time.time() - _start_time
    threshold = get_threshold()
    mode = str(get_config("mode", "popup")).lower()

    success = not _detect_failure()

    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith("<"))
    is_ipython = "IPython" in sys.modules or "ipykernel" in sys.modules

    try:
        import multiprocessing
        if multiprocessing.current_process().name != "MainProcess":
            return
    except Exception:
        pass

    if elapsed > threshold and is_script and not is_ipython:
        script_name = os.path.basename(sys.argv[0])
        status_text = "finished" if success else "FAILED"
        msg = f"'{script_name}' {status_text} in {elapsed:.1f}s"

        # Local notification
        if mode == "sound":
            play_sound(success=success)
        else:
            show_popup(msg, success=success)

        # Remote notification
        logs = _interceptor.get_logs() if _interceptor else []
        
        remote_msg = msg
        if logs:
            remote_msg += f"\n\nRecent output:\n" + "\n".join(logs)
        
        send_remote_notification(remote_msg, title=f"Python Script {status_text.upper()}", success=success)

        prefix = "[SUCCESS]" if success else "[FAILED]"
        print(f"\n{prefix} [pynotify-auto] {msg}")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

_hook_registered = False
_start_time = time.time() 
hook_active = False

def install_hook():
    """Activate the exit hook, wrap sys.exit, and start heartbeat."""
    global _hook_registered, hook_active, _start_time, _exit_code, _interceptor

    if _hook_registered:
        return

    # Skip if disabled or in inappropriate environments
    if get_config("disable") == "1" or get_config("disable") is True:
        return

    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith("<"))
    is_ipython = "IPython" in sys.modules or "ipykernel" in sys.modules
    
    try:
        import multiprocessing
        if multiprocessing.current_process().name != "MainProcess":
            return
    except Exception:
        pass

    if not is_script or is_ipython:
        return

    _hook_registered = True
    hook_active = True
    _start_time = time.time()

    # Capture exit codes
    _original_exit = sys.exit
    def _capturing_exit(code=0):
        global _exit_code
        _exit_code = code
        _original_exit(code)
    sys.exit = _capturing_exit

    # Set up stream interception if remote backend is enabled
    if get_config("remote_backend"):
        max_lines = get_config("log_lines", 10)
        _interceptor = StreamInterceptor(sys.stdout, max_lines=max_lines)
        sys.stdout = _interceptor
        sys.stderr = _interceptor # Shared interceptor for interleaved logs
        
        # Start heartbeat thread
        t = threading.Thread(target=_heartbeat_loop, daemon=True)
        t.start()

    atexit.register(_ping_on_exit)
