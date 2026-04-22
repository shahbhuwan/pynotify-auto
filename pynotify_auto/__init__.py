import atexit
import time
import sys
import os
import subprocess

# Record the start time as soon as the module is imported
_start_time = time.time()

def _get_config(key, default):
    """Get configuration from environment variables."""
    return os.environ.get(f"PYNOTIFY_{key.upper()}", default)

def _get_threshold():
    try:
        return float(_get_config("threshold", 5.0))
    except (ValueError, TypeError):
        return 5.0

def _play_sound(success=True):
    """Play a notification sound based on the platform and status."""
    try:
        if sys.platform == "win32":
            import winsound
            # Use different system sounds for success vs failure
            tone = winsound.MB_ICONASTERISK if success else winsound.MB_ICONHAND
            winsound.MessageBeep(tone)
        elif sys.platform == "darwin":
            # macOS sounds
            sound = "/System/Library/Sounds/Glass.aiff" if success else "/System/Library/Sounds/Basso.aiff"
            subprocess.run(["afplay", sound], check=False)
        else:
            # Linux: try common beep or play command
            subprocess.run(["beep"], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def _show_popup(msg, success=True):
    """Show a system notification popup with status indicators."""
    icon = "✅" if success else "❌"
    title = f"{icon} Python Task {'Finished' if success else 'Failed'}"
    try:
        if sys.platform == "win32":
            # Use powershell for a native Windows toast notification
            # We escape the message for PowerShell
            safe_msg = msg.replace('"', '""')
            ps_script = f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); $notify = new-object system.windows.forms.notifyicon; $notify.icon = [system.drawing.systemicons]::Information; $notify.visible = $true; $notify.showballoontip(10, "{title}", "{safe_msg}", [system.windows.forms.tooltipicon]::None)'
            subprocess.run(["powershell", "-Command", ps_script], check=False)
        elif sys.platform == "darwin":
            # macOS native notification
            subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], check=False)
        else:
            # Linux native notification
            subprocess.run(["notify-send", title, msg], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# Track if an exception has occurred
_exception_occurred = False

def _exception_handler(exctype, value, traceback):
    global _exception_occurred
    _exception_occurred = True
    # Call the original excepthook
    sys.__excepthook__(exctype, value, traceback)

# Install the exception tracker
sys.excepthook = _exception_handler

def _ping_on_exit():
    """Trigger the notification based on the selected mode and exit status."""
    # Check if disabled
    if _get_config("disable", "0") == "1":
        return

    elapsed = time.time() - _start_time
    threshold = _get_threshold()
    mode = _get_config("mode", "popup").lower()
    
    # Check if the script is exiting due to an error
    exc_type, exc_val, _ = sys.exc_info()
    success = not _exception_occurred and (exc_type is None or (exc_type is SystemExit and exc_val.code == 0))
    
    # Validation logic
    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith('<'))
    is_ipython = 'IPython' in sys.modules or 'ipykernel' in sys.modules
    
    if elapsed > threshold and is_script and not is_ipython:
        script_name = os.path.basename(sys.argv[0])
        status_text = "finished" if success else "FAILED"
        msg = f"'{script_name}' {status_text} in {elapsed:.1f}s"
        
        if mode == "sound":
            _play_sound(success=success)
        else: # Default is popup
            _show_popup(msg, success=success)
            
        # Always print a clean message to console
        # Use text indicators for maximum compatibility with all terminals
        prefix = "[SUCCESS]" if success else "[FAILED]"
        print(f"\n{prefix} [pynotify-auto] {msg}")

def install_hook():
    """Register the notification hook to run at exit."""
    if not hasattr(atexit, "_pynotify_auto_hook_registered"):
        atexit.register(_ping_on_exit)
        setattr(atexit, "_pynotify_auto_hook_registered", True)
