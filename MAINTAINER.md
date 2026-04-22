# Maintainer Guide for pynotify-auto

This file contains instructions for the repository owner on how to build and publish the library to PyPI.

## How to Publish to PyPI

To make this library available to others via `pip install pynotify-auto`:

1.  **Create a PyPI Account**: Register at [pypi.org](https://pypi.org).
2.  **Generate an API Token**: Go to your account settings on PyPI and generate a token for publishing.
3.  **Build the Package**:
    ```bash
    # Install build tools
    pip install build twine
    
    # Generate the distribution files (wheel and sdist)
    python -m build
    ```
4.  **Upload to PyPI**:
    ```bash
    # Upload the contents of the dist/ folder
    python -m twine upload dist/*
    ```

## Automated Testing

The project uses GitHub Actions (see `.github/workflows/test.yml`). Every push to GitHub will automatically run the test suite on:
- Windows (latest)
- macOS (latest)
- Ubuntu (latest)
- Python versions 3.8 to 3.12

Ensure that the tests pass before publishing a new version to PyPI.
