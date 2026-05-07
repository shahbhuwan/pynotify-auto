# Tutorial vignette: pynotify-auto walkthrough

This is a **hands-on vignette**—step by step, with expected results and troubleshooting—covering install, the zero-code hook, **all configurable settings** (threshold, mode, remote backends, progress interval, log capture), **Ntfy** and **Telegram**, and the CLI.

**See also:** [README](../README.md) · [Documentation site](https://shahbhuwan.github.io/pynotify-auto/)

---

## What you get (feature overview)

| Capability | How |
|------------|-----|
| Desktop alerts when a script exits | Native notifications (Windows / macOS / Linux) or **sound-only** mode |
| Optional **phone** alerts | **Ntfy** or **Telegram** (only remote backends built in today) |
| Skip tiny runs | **Threshold** (minimum runtime in seconds before notifying) |
| Long runs away from the desk | Periodic **progress** messages to the remote backend with recent log lines |
| Finish / crash awareness | Exit notification; failures and tracebacks can be included in remote payloads |
| No edits to each script | **`pynotify-auto --enable`** installs a `.pth` hook for the active environment |

There are **no other built-in remote providers** (Slack, Discord, email, etc.) at this time; those would be **contributions** or a separate integration layer. Apprise-style breadth is **not** duplicated here—the focus is zero-code + desktop + Ntfy/Telegram.

---

## Prerequisites

- Python **≥ 3.8**
- OS notifications allowed for your terminal (Windows / macOS / Linux)
- For **Ntfy**: an app or browser client subscribed to your topic  
- For **Telegram**: a bot from [@BotFather](https://t.me/BotFather) and your chat ID

---

## Part 1 — Install and enable the hook

### 1.1 Install

```bash
pip install pynotify-auto
pynotify-auto --version
```

### 1.2 Enable zero-code mode (once per environment)

```bash
pynotify-auto --enable
```

You should see where the `pynotify-auto.pth` file was written (under that environment’s **site-packages**).

**Why:** The hook runs when Python starts so your scripts do not need `import pynotify_auto`. If you use **venv or conda**, run `--enable` again when you create a **new** environment.

### 1.3 Smoke test

Default **threshold** is **5 seconds**. Run something slightly longer:

```bash
python -c "import time; time.sleep(6)"
```

You should get a **local** notification (or sound—see **mode** below) when the process exits.

### If nothing fires

- Run `pynotify-auto --info` — **Hook Active** must be **YES**.
- Re-run `pynotify-auto --enable` in the **same** environment you use to run the script.
- Turn off OS **Focus / Do Not Disturb**.
- Ensure runtime **exceeds** the configured threshold.

---

## Part 2 — Local behavior: threshold and mode

### 2.1 Threshold (minimum seconds before “finished” alert)

Only runs that last **longer than** this value trigger the exit notification.

| Where to set | Key / variable |
|--------------|----------------|
| Config file `~/.pynotify.json` | `"threshold": 5.0` |
| Environment | `PYNOTIFY_THRESHOLD` |
| Interactive wizard | `pynotify-auto --config` (prompt **Min. runtime (seconds)**) |

**Examples**

```bash
# One-shot: very sensitive (1 second)
set PYNOTIFY_THRESHOLD=1
python -c "import time; time.sleep(2)"
```

On PowerShell use `$env:PYNOTIFY_THRESHOLD="1"` instead of `set`.

### 2.2 Mode: popup vs sound

| Value | Behavior |
|-------|----------|
| `popup` (default) | Native toast / notification banner |
| `sound` | System beep / chime only (no balloon) |

| Where to set | Key / variable |
|--------------|----------------|
| `~/.pynotify.json` | `"mode": "popup"` or `"sound"` |
| Environment | `PYNOTIFY_MODE` |

---

## Part 3 — Configuration file (`~/.pynotify.json`)

All persistent settings live in **`~/.pynotify.json`** (your user home). You can edit JSON directly or use `pynotify-auto --config` for remote-related fields and some globals.

**Defaults (conceptually)**

```json
{
  "remote_backend": null,
  "ntfy_topic": null,
  "telegram_bot_token": null,
  "telegram_chat_id": null,
  "progress_interval_minutes": 30,
  "log_lines": 10,
  "threshold": 5.0,
  "mode": "popup",
  "disable": false
}
```

**Environment variables override** the file when set (see Part 5).

---

## Part 4 — Remote backends: Ntfy and Telegram

Remote delivery uses **only** these two backends today:

| Backend | When `remote_backend` is | Secrets / identifiers |
|---------|---------------------------|------------------------|
| **Ntfy** | `"ntfy"` | `ntfy_topic` — must match a topic you subscribe to in the [Ntfy](https://ntfy.sh/) app |
| **Telegram** | `"telegram"` | `telegram_bot_token`, `telegram_chat_id` |

### 4.1 Interactive setup (recommended)

```bash
pynotify-auto --config
```

You will be prompted to:

1. Choose **ntfy**, **telegram**, or **none**. (*Choosing **none** deletes `~/.pynotify.json` entirely if it exists—including threshold and mode—so prefer editing JSON or env vars if you only want to turn remote off.*)
2. Enter topic or Telegram credentials.
3. Set **progress interval** (minutes between “still running” phone updates).
4. Set **threshold** (same minimum runtime as Part 2).

### 4.2 Ntfy (step by step)

1. Install the **Ntfy** app (or use the web client).
2. Subscribe to a **unique topic name** (treat it like a secret channel name).
3. Run `pynotify-auto --config`, choose **ntfy**, enter **exactly** that topic.
4. Run `pynotify-auto --test` — you should see a local test plus a push on the topic.

### 4.3 Telegram (step by step)

1. Message **@BotFather** → `/newbot` → copy the **HTTP API token**.
2. Start a chat with your bot; use **@userinfobot** (or similar) to learn your **chat ID**.
3. Run `pynotify-auto --config`, choose **telegram**, paste token and chat ID.
4. Run `pynotify-auto --test`.

### 4.4 What gets sent remotely

- **On exit** (if threshold exceeded): summary line plus optional **recent stdout/stderr** lines (`log_lines`).
- **While running** (if `progress_interval_minutes` **> 0**): periodic **progress** messages with recent log snapshot.
- **Setting `progress_interval_minutes` to `0`** disables the background heartbeat (no periodic pings); **finish/crash** alerts still follow your threshold and remote backend settings.

### 4.5 “Other services” (Slack, Discord, email, …)

Not shipped in core. Use upstream tools (e.g. Apprise) inside your own code, or contribute a backend—see [Contributing](contributing.md).

---

## Part 5 — Environment variable reference

Overrides apply for **keys defined in config** (see `pynotify_auto/config.py`). Documented mapping:

| Setting | JSON key | Environment variable | Default |
|---------|-----------|------------------------|---------|
| Threshold (seconds) | `threshold` | `PYNOTIFY_THRESHOLD` | `5.0` |
| Progress interval (minutes; `0` = no periodic remote pings) | `progress_interval_minutes` | `PYNOTIFY_PROGRESS_INTERVAL` | `30` |
| Lines of log to attach | `log_lines` | `PYNOTIFY_LOG_LINES` | `10` |
| Local mode | `mode` | `PYNOTIFY_MODE` | `popup` |
| Disable all hook behavior | `disable` | `PYNOTIFY_DISABLE` | `false` |
| Remote backend | `remote_backend` | `PYNOTIFY_REMOTE_BACKEND` | unset / `null` |
| Ntfy topic | `ntfy_topic` | `PYNOTIFY_NTFY_TOPIC` | unset |
| Telegram bot token | `telegram_bot_token` | `PYNOTIFY_TELEGRAM_TOKEN` | unset |
| Telegram chat ID | `telegram_chat_id` | `PYNOTIFY_TELEGRAM_CHAT_ID` | unset |

Use `PYNOTIFY_DISABLE=1` for one-off runs without notifications.

---

## Part 6 — CLI commands

| Command | Purpose |
|---------|---------|
| `pynotify-auto --enable` | Install `.pth` hook for this environment |
| `pynotify-auto --info` | Show hook status, mode, threshold, remote backend |
| `pynotify-auto --config` | Interactive Ntfy/Telegram/interval/threshold setup |
| `pynotify-auto --test` | Fire local notification + remote test if configured |
| `pynotify-auto --version` | Print version |
| `pynotify-auto --help` | Help |

---

## Part 7 — Quick reference checklist

```text
pip install pynotify-auto
pynotify-auto --enable
pynotify-auto --info

# Local tuning
# ~/.pynotify.json → "threshold", "mode"
# or PYNOTIFY_THRESHOLD, PYNOTIFY_MODE

# Remote (Ntfy or Telegram only)
pynotify-auto --config
pynotify-auto --test

# Silence everything for one session
set PYNOTIFY_DISABLE=1
```

---

## Vignette outcomes

After working through this document you should be able to:

1. Enable and verify the hook (`--enable`, `--info`).  
2. Tune **threshold** and **mode** (file or env).  
3. Configure **Ntfy** or **Telegram** via `--config` or JSON + env.  
4. Adjust **progress interval** and **log_lines** for long jobs.  
5. Know which features exist today and what requires **other tools** or **contributions**.

---

*Found an inaccuracy? Open an issue or PR against this vignette.*
