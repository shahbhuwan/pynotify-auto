#!/bin/bash

echo "=========================================="
echo "  pynotify-auto Installer"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 could not be found. Please install Python 3."
    exit 1
fi

echo "[1/2] Installing package via pip..."
python3 -m pip install .

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Installation failed."
    exit 1
fi

echo "[2/2] Finalizing configuration..."
# Ensure the .pth file is in site-packages
SITE_PACKAGES=$(python3 -m site --user-site)
mkdir -p "$SITE_PACKAGES"
cp pynotify-auto.pth "$SITE_PACKAGES/"

echo ""
echo "=========================================="
echo "  SUCCESS: pynotify-auto is installed!"
echo "=========================================="
echo "Every Python script you run will now notify"
echo "you if it runs for more than 5 seconds."
echo ""
echo "Configuration:"
echo "- Default: Popup (includes sound)"
echo "- Change Mode: export PYNOTIFY_MODE=sound"
echo ""
