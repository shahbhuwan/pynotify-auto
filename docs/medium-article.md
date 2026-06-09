# Stop Babysitting Your Terminal: Automate Python Notifications with pynotify-auto

![pynotify-auto Banner](banner_pynotify.png)

If you are a data scientist, researcher, or developer, you know the feeling. You hit `Enter` on a long-running script—a model training, a web scrape, or a massive data migration—and then you wait. 

You tab away to check emails, browse Reddit, or grab a coffee. Every few minutes, you tab back to the terminal just to see if it’s still spinning or if it crashed five minutes ago. 

We’ve all been there. And while there are plenty of notification libraries out there, most of them require you to **edit your code**. You have to `import`, you have to `decorate`, and you have to remember to do it for every single script you write.

What if your Python environment was just… *smarter*?

Enter **[pynotify-auto](https://github.com/shahbhuwan/pynotify-auto)**.

---

## The "Zero-Code" Philosophy

The core idea behind `pynotify-auto` is simple: **Notifications should be a feature of your environment, not a burden on your codebase.**

Once installed and enabled, `pynotify-auto` hooks into the Python interpreter itself. It watches your scripts and alerts you when they finish or fail—without you ever typing `import pynotify` in your `.py` files.

### Why this matters:
*   **No Code Pollution**: Your scripts stay clean and focused on their actual logic.
*   **Instant Legacy Support**: It works for scripts you wrote three years ago just as well as the one you’re writing today.
*   **Universal Fail-Safes**: If a script crashes with an unhandled exception, you get an alert with the traceback sent straight to your phone.

---

## Key Features That Make Life Easier

### 1. Smart Thresholding
Nobody wants a notification every time they run `ls` or a quick 1-second utility script. By default, `pynotify-auto` stays quiet unless a script runs for more than 5 seconds (configurable). It only pings you for the tasks that actually give you enough time to walk away.

### 2. Native Desktop Alerts
Whether you’re on **Windows (Toast)**, **macOS (Notification Center)**, or **Linux (Libnotify)**, you get native, sleek popups. No custom GUI windows or clunky consoles.

### 3. Remote Alerts (Ntfy & Telegram)
Need to step away from your desk? `pynotify-auto` supports **Ntfy.sh** (zero-signup required!) and **Telegram**. It can even send you periodic "heartbeat" updates for multi-hour jobs, including a snapshot of the last few lines of your logs so you can check progress from your phone.

---

## Getting Started in 60 Seconds

### Step 1: Install
```bash
pip install pynotify-auto
```

### Step 2: Enable the Hook
This is the "magic" step that tells your current Python environment to monitor scripts automatically.
```bash
pynotify-auto --enable
```

### Step 3: Configure (Optional)
Want phone alerts? Use the interactive wizard:
```bash
pynotify-auto --config
```

### Step 4: Forget It Exists
Run your scripts as usual. If one takes longer than 5 seconds, you’ll get a chime and a popup when it’s done.

---

## Where does it fit?

There are several great notification libraries for Python, but they serve different needs. Here is how they compare:

*   **Apprise / Plyer**: Best for **Production Apps**. These are powerful APIs where you explicitly control every notification.
    *   *Integration*: Manual code and imports in every file.
    *   *Setup*: High (requires editing every script).
*   **knockknock**: Best for **ML Training**. Uses decorators to wrap specific long-running functions.
    *   *Integration*: Function decorators.
    *   *Setup*: Medium (requires wrapping entry points).
*   **pynotify-auto**: Best for **General Developer Productivity**. It’s the only "set it and forget it" solution.
    *   *Integration*: **Zero-Code (Automatic Hook)**.
    *   *Setup*: **Low** (Install once per environment and you're done).

---

## Final Thoughts

We spend enough time debugging and writing code; we shouldn't have to spend more time managing our notifications. `pynotify-auto` was built to solve the "babysitting" problem once and for all.

**Check it out on GitHub:** [https://github.com/shahbhuwan/pynotify-auto](https://github.com/shahbhuwan/pynotify-auto)

---

*I'm always looking to improve the tool! If you have ideas for new backends (Slack, Discord, etc.) or features, feel free to open a PR or an issue.*
