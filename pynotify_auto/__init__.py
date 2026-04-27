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

__version__ = "0.3.1"

def get_config(key, default):
    """Read PYNOTIFY_* environment variables."""
    return os.environ.get(f"PYNOTIFY_{key.upper()}", default)


def get_threshold():
    """Get threshold in seconds (default 5.0)."""
    try:
        return float(get_config("threshold", 5.0))
    except (ValueError, TypeError):
        return 5.0


# ---------------------------------------------------------------------------
# Notification back-ends
# ---------------------------------------------------------------------------

def play_sound(success=True):
    """Play a system chime based on exit status."""
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
    icon = "\u2705" if success else "\u274c"
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
            subprocess.run(
                ["powershell", "-Command", ps_script],
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif sys.platform == "darwin":
            subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], check=False)
        else:
            subprocess.run(["notify-send", title, msg], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Failure tracking
# ---------------------------------------------------------------------------

# Detecting failure at atexit is annoying in CPython:
# 1. sys.excepthook isn't called for SystemExit.
# 2. sys.last_type is only set for tracebacks.
# 3. sys.exc_info() is empty inside atexit handlers.
#
# Solution: wrap sys.exit() to grab the code, and use sys.last_type as a backup.
_exit_code = None

def _detect_failure():
    """True if we're exiting due to a crash or non-zero sys.exit()."""
    global _exit_code

    # If sys.exit was called, use that code
    if _exit_code is not None:
        return _exit_code not in (0, None)

    # Otherwise check if an unhandled exception set the global last_type
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
    if get_config("disable", "0") == "1":
        return

    elapsed = time.time() - _start_time
    threshold = get_threshold()
    mode = get_config("mode", "popup").lower()

    success = not _detect_failure()

    # Skip for REPL/IPython or internal scripts
    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith("<"))
    is_ipython = "IPython" in sys.modules or "ipykernel" in sys.modules

    # Only notify from the main process
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

        if mode == "sound":
            play_sound(success=success)
        else:
            show_popup(msg, success=success)

        prefix = "[SUCCESS]" if success else "[FAILED]"
        print(f"\n{prefix} [pynotify-auto] {msg}")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

_hook_registered = False
_start_time = time.time() 
hook_active = False

def install_hook():
    """Activate the exit hook and wrap sys.exit."""
    global _hook_registered, hook_active, _start_time, _exit_code

    if _hook_registered:
        return

    _hook_registered = True
    hook_active = True
    _start_time = time.time()

    # Capture exit codes since SystemExit is invisible to excepthook/atexit
    _original_exit = sys.exit
    def _capturing_exit(code=0):
        global _exit_code
        _exit_code = code
        _original_exit(code)
    sys.exit = _capturing_exit

    atexit.register(_ping_on_exit)
