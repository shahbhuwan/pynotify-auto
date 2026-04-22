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

def _play_sound():
    """Play a notification sound based on the platform."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sys.platform == "darwin":
            # macOS default alert sound
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
        else:
            # Linux: try common beep or play command
            subprocess.run(["beep"], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def _show_popup(msg):
    """Show a system notification popup."""
    title = "Python Task Finished"
    try:
        if sys.platform == "win32":
            # Use powershell for a native Windows toast notification without extra dependencies
            ps_script = f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); [reflection.assembly]::loadwithpartialname("System.Drawing"); $notify = new-object system.windows.forms.notifyicon; $notify.icon = [system.drawing.systemicons]::Information; $notify.visible = $true; $notify.showballoontip(10, "{title}", "{msg}", [system.windows.forms.tooltipicon]::None)'
            subprocess.run(["powershell", "-Command", ps_script], check=False)
        elif sys.platform == "darwin":
            # macOS native notification
            subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], check=False)
        else:
            # Linux native notification
            subprocess.run(["notify-send", title, msg], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def _ping_on_exit():
    """Trigger the notification based on the selected mode."""
    # Check if disabled
    if _get_config("disable", "0") == "1":
        return

    elapsed = time.time() - _start_time
    threshold = _get_threshold()
    mode = _get_config("mode", "popup").lower() # sound, popup (default)
    
    # Validation logic
    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith('<'))
    is_ipython = 'IPython' in sys.modules or 'ipykernel' in sys.modules
    
    if elapsed > threshold and is_script and not is_ipython:
        script_name = os.path.basename(sys.argv[0])
        msg = f"'{script_name}' finished in {elapsed:.1f}s"
        
        if mode == "sound":
            _play_sound()
        else: # Default is popup (which usually includes sound)
            _show_popup(msg)
            
        # Always print a clean message to console
        print(f"\n[pynotify-auto] {msg}")

def install_hook():
    """Register the notification hook to run at exit."""
    if not hasattr(atexit, "_pynotify_auto_hook_registered"):
        atexit.register(_ping_on_exit)
        setattr(atexit, "_pynotify_auto_hook_registered", True)
