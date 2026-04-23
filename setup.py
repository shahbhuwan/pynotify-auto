from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pynotify-auto",
    version="0.2.5",
    author="Bhuwan Shah",
    description="Zero-Code automatic notifications for long-running Python scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shahbhuwan/pynotify-auto",
    packages=find_packages(),
    include_package_data=True,
    # This ensures the .pth file is placed in the correct site-packages
    # On Windows, this is 'Lib/site-packages'. On others, it's relative to site-packages.
    data_files=[
        ('Lib/site-packages' if os.name == 'nt' else '.', ['pynotify-auto.pth'])
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "pynotify-auto=pynotify_auto.cli:main",
        ],
    },
)
