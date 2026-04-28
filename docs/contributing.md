# Contributing

We welcome contributions! 

## Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Install dependencies and dev tools.
4. Create a new branch for your feature or bugfix.

## Running Tests

We use a comprehensive test suite to ensure stability.

```bash
python -m unittest tests/test_comprehensive.py
```

## Adding New Backends

If you'd like to add a new notification backend (e.g., Slack, Discord, Pushover):

1. Add the logic to `pynotify_auto/__init__.py`.
2. Add a configuration option to toggle it.
3. Update the documentation.
4. Submit a Pull Request!
