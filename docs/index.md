# Welcome to pynotify-auto

**Know when your Python scripts finish or fail.**

Get alerts on your computer or on your phone when a run completes or crashes—so you can step away from your desk. Install once; nothing to import or add to your scripts.

Stop babysitting your terminal. Whether you're training models, processing datasets, or running complex simulations, `pynotify-auto` pings you the moment your task is done—so you can focus on what matters.

## Key Features

- **Zero-Code Integration**: Works automatically across your entire system/environment.
- **Smart Thresholding**: Only pings if the script ran for a meaningful amount of time (default > 5s).
- **Cross-Platform**: Works on Windows, macOS, and Linux.
- **Configurable**: Change the threshold or disable it via environment variables.

## Why pynotify-auto?

Traditional notification libraries require you to manually add decorators or extra lines of code to every script. `pynotify-auto` is different: **it works automatically for every script in your environment.** 

- **No Code Changes**: Install once, and it works for all your scripts.
- **Smart Filtering**: It stays quiet for quick tasks and only alerts you for the ones that actually take time.
- **Immediate Feedback**: Know exactly when your process finishes or fails, even if you're in another room.

## Quick Start

```bash
pip install pynotify-auto
pynotify-auto --enable
```

Try running a long process:

```bash
python -c "import time; time.sleep(6)"
```

You should receive a notification!

## Compared to other libraries

See **[Comparison](COMPARISON.md)** for how `pynotify-auto` differs from Apprise, Plyer, notifiers, and knockknock.

## Tutorial vignette

Follow **[tutorial-vignette.md](tutorial-vignette.md)** for a complete hands-on walkthrough: install, thresholds, local modes, Ntfy and Telegram, progress interval, and environment variables.
