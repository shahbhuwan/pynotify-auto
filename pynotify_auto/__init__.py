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

__version__ = "0.5.6"

_config = cfg_module.load_config()

def get_config(key, default=None):
    """Read config with fallback. Checks environment variables dynamically."""
    # Mapping of short env var names used in README to internal config keys
    mapping = {
        "threshold": "PYNOTIFY_THRESHOLD",
        "progress_interval_minutes": "PYNOTIFY_PROGRESS_INTERVAL",
        "log_lines": "PYNOTIFY_LOG_LINES",
        "mode": "PYNOTIFY_MODE",
        "disable": "PYNOTIFY_DISABLE",
        "remote_backend": "PYNOTIFY_REMOTE_BACKEND",
        "ntfy_topic": "PYNOTIFY_NTFY_TOPIC",
        "telegram_bot_token": "PYNOTIFY_TELEGRAM_TOKEN",
        "telegram_chat_id": "PYNOTIFY_TELEGRAM_CHAT_ID",
    }
    
    env_key = mapping.get(key, f"PYNOTIFY_{key.upper()}")
    env_val = os.environ.get(env_key)
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
            # Use the proven NotifyIcon method for maximum compatibility
            ps_script = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$t = New-Object System.Windows.Forms.NotifyIcon; "
                f"$t.Icon = [System.Drawing.SystemIcons]::Information; "
                f"$t.Visible = $true; "
                f'$t.ShowBalloonTip(5000, "{title}", "{safe_msg}", [System.Windows.Forms.ToolTipIcon]::Info); '
                f"Start-Sleep 5"
            )
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

class LogInterceptor:
    """Captures all output at the OS File Descriptor level (FD 1 and 2).
    This ensures we capture output from multiprocessing workers, C extensions, 
    and subprocesses that bypass sys.stdout.
    """
    def __init__(self, max_lines=10):
        self.log_history = deque(maxlen=max_lines)
        self._lock = threading.Lock()
        
        try:
            # Save original stdout to write back to the console
            self.orig_stdout_fd = os.dup(sys.stdout.fileno())
            
            # Create pipe for interception
            self.pipe_r, self.pipe_w = os.pipe()
            
            # Redirect stdout/stderr at FD level
            os.dup2(self.pipe_w, sys.stdout.fileno())
            os.dup2(self.pipe_w, sys.stderr.fileno())
            
            # Start reader thread
            self.thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.thread.start()
        except Exception:
            pass

    def _reader_loop(self):
        while True:
            try:
                data = os.read(self.pipe_r, 4096)
                if not data: # EOF
                    break
                
                # Echo to original console
                os.write(self.orig_stdout_fd, data)
                
                # Update history
                try:
                    text = data.decode('utf-8', errors='replace')
                    for line in text.splitlines():
                        if line.strip():
                            with self._lock:
                                timestamp = time.strftime("%H:%M:%S")
                                self.log_history.append(f"[{timestamp}] {line.strip()}")
                except Exception:
                    pass
            except Exception:
                break

    def stop(self):
        """Restore FDs and wait for reader thread to flush."""
        try:
            # Restore original FDs first so subsequent prints don't go to closed pipe
            os.dup2(self.orig_stdout_fd, 1)
            os.dup2(self.orig_stdout_fd, 2)
            # Close pipe write end to trigger EOF in reader thread
            os.close(self.pipe_w)
            self.thread.join(timeout=1.0)
            os.close(self.pipe_r)
            os.close(self.orig_stdout_fd)
        except Exception:
            pass

    def get_logs(self):
        with self._lock:
            return list(self.log_history)

    def flush(self):
        pass

    def __getattr__(self, name):
        # Compatibility for anything looking for sys.stdout/stderr attributes
        return getattr(sys.__stdout__, name)


class _TeeStream:
    """Wrap the real console streams and copy non-empty lines into log_history.

    Must never raise from ``write`` / ``flush``: ``print(..., flush=True)`` and IDEs
    assume stdout is reliable. Do **not** call ``flush()`` inside ``write`` — Python's
    ``print`` already calls ``flush`` after ``write``; double-flushing the Windows
    console often raises ``OSError`` (WinError 1 / 22).
    """

    def __init__(self, base, history: deque, lock: threading.Lock):
        self._base = base
        self._history = history
        self._lock = lock

    def write(self, s):
        if not s:
            return 0
        if isinstance(s, bytes):
            s = s.decode("utf-8", errors="replace")
        n = len(s)
        try:
            self._base.write(s)
        except (OSError, IOError, ValueError, RuntimeError):
            # Still report success so ``print`` / logging do not abort the host script.
            pass
        except Exception:
            pass
        try:
            for line in str(s).splitlines():
                line = line.strip()
                if line:
                    with self._lock:
                        ts = time.strftime("%H:%M:%S")
                        self._history.append(f"[{ts}] {line}")
        except Exception:
            pass
        return n

    def flush(self):
        try:
            self._base.flush()
        except (OSError, IOError, ValueError, RuntimeError):
            pass
        except Exception:
            pass

    def fileno(self):
        try:
            return self._base.fileno()
        except (OSError, AttributeError, ValueError):
            return -1

    def isatty(self):
        try:
            return self._base.isatty()
        except Exception:
            return False

    @property
    def encoding(self):
        return getattr(self._base, "encoding", "utf-8")

    @property
    def errors(self):
        return getattr(self._base, "errors", "replace")

    def __getattr__(self, name):
        return getattr(self._base, name)


class PythonTeeInterceptor:
    """Windows-safe capture for remote logs: tee via sys.stdout/sys.stderr only.

    FD-level ``dup2`` redirection breaks the Windows console (OSError 22
    'Incorrect function') for tracebacks and some IDE hooks; see LogInterceptor.
    """

    def __init__(self, max_lines=10):
        self.log_history = deque(maxlen=max_lines)
        self._lock = threading.Lock()
        self._saved_stdout = sys.stdout
        self._saved_stderr = sys.stderr
        sys.stdout = _TeeStream(sys.__stdout__, self.log_history, self._lock)
        sys.stderr = _TeeStream(sys.__stderr__, self.log_history, self._lock)

    def stop(self):
        try:
            sys.stdout = self._saved_stdout
            sys.stderr = self._saved_stderr
        except Exception:
            pass

    def get_logs(self):
        with self._lock:
            return list(self.log_history)

    def flush(self):
        pass


_interceptor = None


def _stderr_from_fd_redirect() -> bool:
    """True if LogInterceptor replaced FDs (has dup'd console fd)."""
    global _interceptor
    return bool(
        _interceptor
        and getattr(_interceptor, "orig_stdout_fd", None) is not None
    )


def _looks_like_pytest_runtime() -> bool:
    """Avoid background heartbeat during pytest (capture / Win access violations)."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    if "_pytest" in sys.modules or "pytest" in sys.modules:
        return True
    args = sys.argv
    if "-m" in args and any(a == "pytest" for a in args):
        return True
    try:
        return os.path.basename(sys.argv[0]).lower().startswith("pytest")
    except Exception:
        return False


def _looks_like_packaging_cli() -> bool:
    """pip/conda/uv attach pipes to stdout/stderr; tee wrappers break them (OSError 22, broken pipe)."""
    argv = sys.argv
    if not argv:
        return False
    try:
        base = os.path.basename(argv[0]).lower()
    except Exception:
        return False
    # pip.exe, pip3.exe, conda.exe, uv.exe, poetry.exe, ...
    exe_prefixes = (
        "pip",
        "conda",
        "conda-env",
        "micromamba",
        "mamba",
        "uv",
        "poetry",
        "pdm",
        "hatch",
        "twine",
        "wheel",
    )
    for p in exe_prefixes:
        if base == p + ".exe" or base.startswith(p + ".") or base == p:
            return True
    # python.exe -m pip / -m ensurepip / -m build / ...
    if "-m" in argv:
        try:
            mi = argv.index("-m")
            if mi + 1 < len(argv):
                root_mod = argv[mi + 1].split(".")[0].lower()
                if root_mod in (
                    "pip",
                    "ensurepip",
                    "venv",
                    "build",
                    "installer",
                    "wheel",
                    "twine",
                    "setuptools",
                ):
                    return True
        except ValueError:
            pass
    # python setup.py ...
    if any("setup.py" in (a or "") for a in argv[1:6]):
        return True
    return False


def _safe_status_line(message: str) -> None:
    """Write hook status without going through replaced sys.stdout (tee / capture safe)."""
    text = f"\n[pynotify-auto] {message}\n"
    data = text.encode("utf-8", errors="replace")
    try:
        if _stderr_from_fd_redirect():
            os.write(_interceptor.orig_stdout_fd, data)
            return
    except Exception:
        pass
    try:
        out = sys.__stdout__
        out.write(text)
        out.flush()
    except Exception:
        pass


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

    def _status_msg(m):
        _safe_status_line(m)

    _status_msg(f"Remote updates active. Next update in {interval/60:.1f} minutes.")
    
    while True:
        time.sleep(interval)
        if not _interceptor:
            continue
            
        logs = _interceptor.get_logs()
        
        if logs:
            log_text = "\n".join(logs)
            msg = f"Still running...\n\nRecent output:\n{log_text}"
            _status_msg(f"Sending progress update to phone ({get_config('remote_backend')})...")
            success = send_remote_notification(msg, title=f"Progress: {script_name}", success=True)
            if not success:
                 _status_msg("⚠️ Remote update failed (check connection/topic)")


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
        _safe_status_line(f"{prefix} {msg}")

    if _interceptor:
        _interceptor.stop()


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

    if _looks_like_packaging_cli():
        return

    # 🛑 NESTED SUPPRESSION
    # If a parent process is already handling notifications, the child should stay silent.
    active_pid = os.environ.get("PYNOTIFY_ACTIVE_PID")
    if active_pid and active_pid != str(os.getpid()):
        return
    
    # Mark this PID as the active notifier for all children
    os.environ["PYNOTIFY_ACTIVE_PID"] = str(os.getpid())

    # 🛑 MULTIPROCESSING SUPPRESSION
    # On Windows, workers start with '-c' and '--multiprocessing-fork' or 'spawn_main'
    if len(sys.argv) > 1 and sys.argv[0] == "-c":
        arg_str = " ".join(sys.argv)
        if "multiprocessing" in arg_str or "spawn_main" in arg_str or "ipykernel" in arg_str:
            return

    # Skip if disabled or in inappropriate environments
    if get_config("disable") == "1" or get_config("disable") is True:
        return

    is_script = bool(sys.argv and sys.argv[0] and not sys.argv[0].startswith("<"))
    is_ipython = "IPython" in sys.modules or "ipykernel" in sys.modules
    
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

    # Capture script output for remote "recent logs" feature.
    # On Windows, FD-level dup2 breaks the console (tracebacks → OSError 22).
    if get_config("remote_backend"):
        max_lines = get_config("log_lines", 10)
        if sys.platform == "win32":
            _interceptor = PythonTeeInterceptor(max_lines=max_lines)
        else:
            _interceptor = LogInterceptor(max_lines=max_lines)

        if not _looks_like_pytest_runtime():
            t = threading.Thread(target=_heartbeat_loop, daemon=True)
            t.start()

    atexit.register(_ping_on_exit)
