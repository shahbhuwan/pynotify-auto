# Installation

## Via Pip

```bash
pip install pynotify-auto
```

## Activation Step

Due to how modern Python environments (Conda, venv) handle installation, you may need to manually enable the zero-code hook once after installation:

```bash
pynotify-auto --enable
```

This ensures that `pynotify-auto` can monitor your scripts automatically. You can check the status at any time with `pynotify-auto --info`.

## Conda & Virtual Environments

Always install this library while your environment is **active**. If you find that notifications aren't working, run:

```bash
pynotify-auto --enable
```

to verify the hook is installed inside your isolated environment.
