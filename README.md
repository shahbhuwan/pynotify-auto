# pynotify-auto 🚀

**Zero-Code automatic notifications for long-running Python scripts.**

Tired of checking your terminal every 5 minutes to see if your script finished? `pynotify-auto` automatically pings you (with a sound and a system notification) when any Python script runs for more than 5 seconds.

**No code changes required.** Just install and forget.

## Features

- **Zero-Code Integration**: Works automatically across your entire system/environment.
- **Smart Thresholding**: Only pings if the script ran for a meaningful amount of time (default > 5s).
- **Cross-Platform**: Works on Windows, macOS, and Linux.
- **Configurable**: Change the threshold or disable it via environment variables.

## Installation

### Via Pip
```bash
pip install .
```

### Via Conda
(Once uploaded to a channel or built)
```bash
conda install -c your-channel pynotify-auto
```

## How it Works

The library uses a Python Path Configuration file (`.pth`) to register an `atexit` hook during Python startup. This allows it to monitor the execution time of any script without you having to import anything manually.

## Configuration

You can customize the behavior using environment variables:

- `PYNOTIFY_MODE`: Notification type. Options: `popup` (default), `sound`.
- `PYNOTIFY_THRESHOLD`: Minimum execution time in seconds (default: `5.0`).
- `PYNOTIFY_DISABLE`: Set to `1` to disable notifications for a specific run.

### Examples

```bash
# Only get a sound notification (no popup)
export PYNOTIFY_MODE=sound
python training.py

# Only notify if script takes longer than 10 minutes
export PYNOTIFY_THRESHOLD=600
python long_process.py
```

## Command Line Interface (CLI)

Once installed, you can use the `pynotify-auto` command to test your settings:

- `pynotify-auto --test`: Trigger a test notification.
- `pynotify-auto --info`: View current mode and threshold settings.
- `pynotify-auto --help`: Show all available commands.

## License

MIT
