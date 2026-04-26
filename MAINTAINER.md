# Maintainer Guide for pynotify-auto

This file contains instructions for the repository owner on how to build and publish the library to PyPI.

## How to Publish to PyPI (Manual)

To make this library available to others via `pip install pynotify-auto`:

1.  **Create a PyPI Account**: Register at [pypi.org](https://pypi.org).
2.  **Generate an API Token**: Go to your account settings on PyPI and generate a token for publishing.
3.  **Build and Upload**:
    ```bash
    pip install build twine
    python -m build
    python -m twine upload dist/*
    ```

## Automated Publishing (Recommended)

I have set up a GitHub Action (`.github/workflows/publish.yml`) that automates the entire process. 

### One-Time Setup:
1.  Go to your GitHub repository: **Settings** -> **Secrets and variables** -> **Actions**.
2.  Add a **New repository secret**.
3.  Name: `PYPI_API_TOKEN`
4.  Value: (Paste your PyPI API Token here).

### How to trigger an update:
Whenever you want to release a new version online:
1.  **Update the version** in `pyproject.toml` (e.g., change `0.3.0` to `0.3.1`).
2.  **Commit and push** the change.
3.  **Create a tag** and push it:
    ```bash
    git tag v0.1.1
    git push origin v0.1.1
    ```
GitHub will now automatically build and publish the new version to PyPI for you!

## Automated Testing

The project uses GitHub Actions (see `.github/workflows/test.yml`). Every push to GitHub will automatically run the test suite on:
- Windows (latest)
- macOS (latest)
- Ubuntu (latest)
- Python versions 3.8 to 3.12

Ensure that the tests pass before publishing a new version to PyPI.
