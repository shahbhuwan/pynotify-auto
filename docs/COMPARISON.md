# How `pynotify-auto` compares to other Python notification tools

This page compares **pynotify-auto** with several widely used libraries so you can pick the right tool. It is written to be fair: each project optimizes for different goals.

## TL;DR

| Tool | Main idea | Add code to each script? | Typical desktop alert | Typical phone / remote |
|------|-----------|---------------------------|------------------------|-------------------------|
| [**pynotify-auto**](https://pypi.org/project/pynotify-auto/) | Install once, optional `.pth` hook → notify on script exit | **No** (after `pynotify-auto --enable` in that environment) | Native OS toast / notification (Windows, macOS, Linux) | Optional **Ntfy** or **Telegram** + log snapshots |
| [**Apprise**](https://pypi.org/project/apprise/) | One library, many notification URLs | **Yes** — you call `notify()` (or use the CLI) | Possible via plugins / OS; not the core focus | Excellent — 100+ services (Slack, Discord, email, …) |
| [**Plyer**](https://pypi.org/project/plyer/) | Cross-platform facade for mobile/desktop APIs | **Yes** — import and call Plyer in your app | Strong for simple desktop/mobile notifications | Depends on platform APIs you wire up |
| [**notifiers**](https://pypi.org/project/notifiers/) | Unified interface to many providers | **Yes** — API or CLI | Not primary focus | Many providers (Telegram, Pushover, …) |
| [**knockknock**](https://pypi.org/project/knockknock/) | Notify when long jobs finish (often ML / training) | **Yes** — decorators or wrappers around your entrypoints | Usually indirect (email / messaging) | Email and optional channels depending on setup |

---

## What makes `pynotify-auto` different?

Most libraries assume you **control the source** of each script and are happy to add imports, decorators, or `notify()` calls.

**pynotify-auto** targets a different situation:

- You run **many one-off scripts** (analysis, scrapers, batch jobs) and do not want to edit each file.
- You want **finish / failure awareness** without threading notification code through every project.
- You may **leave your desk** and still want alerts (**Ntfy** / **Telegram**) plus optional rolling log snapshots.

Integration is **environment-level**: install the package, run `pynotify-auto --enable` once per virtualenv (or equivalent), and scripts in that environment get exit notifications subject to your threshold and settings.

---

## Library-by-library notes

### Apprise

- **Strengths:** Huge number of backends, mature API, CLI for scripting and automation, great when notifications are a first-class part of your application design.
- **Contrast:** You still **invoke** Apprise from code (or shell out to `apprise`). It does not automatically notify on every arbitrary `python myscript.py` exit unless you add that call or wrapper yourself.

**Use Apprise when:** You want maximum flexibility of channels and are fine adding explicit notification logic (or centralizing it in your own helper).

---

### Plyer

- **Strengths:** Simple cross-platform API for notifications (and other platform features); familiar if you already structure apps around explicit UI/platform calls.
- **Contrast:** Each script or app must **import Plyer and call** the notification APIs.

**Use Plyer when:** You own the codebase and want portable notification calls inside your application.

---

### notifiers

- **Strengths:** Clean unified API and CLI across multiple providers; good for “send this message to Slack/Telegram/email.”
- **Contrast:** Same pattern — **explicit calls** from your code or CLI in your pipeline.

**Use notifiers when:** You want a lighter-weight multi-provider layer than rolling everything yourself, with explicit sends.

---

### knockknock

- **Strengths:** Familiar in ML workflows; decorators like “email me when training completes”; integrates with common training stacks.
- **Contrast:** Designed around **wrapping** training or job entrypoints, not silent global behavior for every Python process in an environment.

**Use knockknock when:** You mainly care about long-running training jobs and are happy to decorate or wrap those functions.

---

## Features unique to `pynotify-auto` (today)

These are intentional design choices; other tools may not aim for them:

| Feature | pynotify-auto |
|--------|----------------|
| No edits to individual scripts | Yes — hook runs when the interpreter loads (per enabled environment) |
| Threshold so trivial runs stay quiet | Yes — default minimum duration before notifying |
| Optional remote **log excerpts** with crashes / progress cadence | Yes — when remote backends are configured |
| 100+ arbitrary backends in one dependency tree | No — focused on **desktop + Ntfy + Telegram** |

---

## Honest limitations of `pynotify-auto`

- **Per-environment setup:** You need `pip install` and **`pynotify-auto --enable`** (and possibly elevated permissions on some global Python installs). This is not “magic on every machine worldwide” without that step.
- **Not a fit for library authors as a hidden dependency:** Shipping a `.pth` hook as a transitive dependency of another library can surprise users; this tool is aimed at **end users / developers** opting in for their own environments.
- **Script-oriented:** Behavior is tuned for running scripts (not primarily for interactive notebooks / IPython).
- **Fewer backends than Apprise:** If you need Microsoft Teams, Discord, Slack, etc., **Apprise** (or a dedicated SDK) is the more natural fit — you can still use `pynotify-auto` locally and Apprise in code if you ever combine both.

---

## Summary

- Choose **Apprise** or **notifiers** when you want **explicit, rich routing** to many services from code you control.
- Choose **Plyer** when you want a **single portable API** inside your app.
- Choose **knockknock** when you want **decorated ML / training** workflows.
- Choose **pynotify-auto** when you want **finish/failure awareness across scripts** with **minimal per-file work**, optional **phone** alerts, and **desktop** integration without editing each script.

---

## See also

- [README](../README.md) — install, `--enable`, remote setup  
- [Documentation site](https://shahbhuwan.github.io/pynotify-auto/)

If you spot a factual error or an important library we should list, open an issue or PR.
