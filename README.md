# pynotify-auto

# **Smart, effortless notifications for your Python scripts.**

## **Stay informed on your desktop or your phone, without changing a single line of code.**

---

### 🌐 [**VIEW LIVE DOCUMENTATION & SETUP GUIDE**](https://shahbhuwan.github.io/pynotify-auto/)

---

[![Documentation](https://img.shields.io/badge/docs-view-brightgreen)](https://shahbhuwan.github.io/pynotify-auto/)
[![PyPI version](https://img.shields.io/pypi/v/pynotify-auto.svg)](https://pypi.org/project/pynotify-auto/)
[![Supported OS](https://img.shields.io/badge/os-Windows%20|%20macOS%20|%20Linux-blue)](https://github.com/shahbhuwan/pynotify-auto)
[![Python Versions](https://img.shields.io/pypi/pyversions/pynotify-auto.svg)](https://pypi.org/project/pynotify-auto/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why use this?
Traditional notification libraries require you to manually add decorators or extra lines of code to every script. `pynotify-auto` is different: **it works automatically for every script in your environment.** 

- **Desktop + Mobile**: Get native popups on your computer and real-time snapshots on your phone (Ntfy/Telegram).
- **Cross-Platform**: Full support for Windows (Toast), macOS (Notification Center), and Linux (Libnotify).
- **Zero-Code Integration**: Install once, and it works for all your scripts globally.
- **Smart Filtering**: It stays quiet for quick tasks and only alerts you for the ones that actually take time.

## Features

- **Zero-Code Integration**: Works automatically across your entire system/environment.
- **Smart Thresholding**: Only pings if the script ran for a meaningful amount of time (default > 5s).
- **Cross-Platform**: Works on Windows, macOS, and Linux.
- **Configurable**: Change the threshold or disable it via environment variables.

## Installation

### Via Pip
```bash
pip install pynotify-auto
```

> [!IMPORTANT]
> **Activation Step**: Due to how modern Python environments (Conda, venv) handle installation, you may need to manually enable the zero-code hook once after installation:
> ```bash
> pynotify-auto --enable
> ```
> This ensures that `pynotify-auto` can monitor your scripts automatically. You can check the status at any time with `pynotify-auto --info`.

## 📱 Remote Notifications (Phone/Mobile)

`pynotify-auto` can track your script's progress and send real-time updates to your phone. It supports **Ntfy.sh** and **Telegram**.

### Interactive Configuration
The easiest way to configure remote alerts is using the built-in wizard:
```bash
pynotify-auto --config
```
This interactive guide will help you choose your service and enter your credentials. It even remembers your settings so you can update them later by just pressing Enter.

### Supported Backends

| Service | Setup Effort | Benefits |
| :--- | :--- | :--- |
| **Ntfy.sh** | ⭐ (Zero Signup) | No account needed, lightweight, instant setup. |
| **Telegram** | ⭐⭐ (Create Bot) | Private, persistent history, premium formatting. |

#### Setting up Ntfy.sh
1. Install the **Ntfy** app on your phone.
2. Subscribe to a unique topic name (e.g., `my_script_alerts`).
3. Run `pynotify-auto --config`, choose `ntfy`, and enter that topic name.

#### Setting up Telegram
1. Message **@BotFather** on Telegram to create a new bot and get your **API Token**.
2. Message **@userinfobot** to get your **Chat ID**.
3. Run `pynotify-auto --config`, choose `telegram`, and enter your Token and Chat ID.

### ⏳ Real-Time Progress Tracking
Once enabled, `pynotify-auto` will automatically:
- **Ping your phone** every 30 minutes (configurable) with a snapshot of your logs.
- Notify you immediately if the script **crashes** with the error traceback.
- Notify you when the script **finishes** successfully.

---

## ⚙️ Advanced Configuration

All settings are stored in `~/.pynotify.json`. You can also override them using environment variables:

| Setting | JSON Key | Env Variable | Default |
| :--- | :--- | :--- | :--- |
| **Threshold** | `threshold` | `PYNOTIFY_THRESHOLD` | `5.0` (sec) |
| **Progress Interval** | `progress_interval_minutes` | `PYNOTIFY_PROGRESS_INTERVAL` | `30` (min) |
| **Log History** | `log_lines` | `PYNOTIFY_LOG_LINES` | `10` |
| **Backend** | `remote_backend` | `PYNOTIFY_REMOTE_BACKEND` | `None` |
| **Ntfy Topic** | `ntfy_topic` | `PYNOTIFY_NTFY_TOPIC" | `None` |
| **Telegram Token** | `telegram_bot_token` | `PYNOTIFY_TELEGRAM_TOKEN` | `None` |
| **Telegram Chat ID** | `telegram_chat_id` | `PYNOTIFY_TELEGRAM_CHAT_ID` | `None` |

The "Zero-Code" progress tracker automatically intercepts your script's output (`stdout` and `stderr`). It captures `print()` statements, standard `logging`, and even crash tracebacks without requiring any changes to your code.


## 🤝 Used By

Are you using `pynotify-auto` in your project? We'd love to feature you here! 
Open a PR to add your project to the list.

## License

MIT

## Contributing

I'm open to contributions! Feel free to fork the repo and open a PR if you have bug fixes or new notification backends (Slack, Discord, etc.) you'd like to add.

Check the [comprehensive test suite](tests/test_comprehensive.py) for examples on how to run tests locally.


