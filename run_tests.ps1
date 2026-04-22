# pynotify-auto Local Test Suite

$PYTHON_EXE = "C:\Software\Anaconda\envs\downsclae_env\python.exe"
$env:PYNOTIFY_THRESHOLD = "2"

Write-Host "`n--- TEST 1: Standard Success (Popup) ---" -ForegroundColor Cyan
& $PYTHON_EXE -c "import time; print('Running success test...'); time.sleep(3)"

Write-Host "`n--- TEST 2: Script Failure (Error Popup) ---" -ForegroundColor Red
& $PYTHON_EXE -c "import time; print('Running failure test...'); time.sleep(3); raise ValueError('Planned Error')"

Write-Host "`n--- TEST 3: Sound-Only Mode ---" -ForegroundColor Yellow
$env:PYNOTIFY_MODE = "sound"
& $PYTHON_EXE -c "import time; print('Running sound-only test...'); time.sleep(3)"
$env:PYNOTIFY_MODE = "popup"

Write-Host "`n--- TEST 4: Threshold Filtering (Should NOT notify) ---" -ForegroundColor Gray
& $PYTHON_EXE -c "import time; print('Running fast script...'); time.sleep(0.5)"

Write-Host "`n--- TEST 5: Disabled Mode (Should NOT notify) ---" -ForegroundColor Gray
$env:PYNOTIFY_DISABLE = "1"
& $PYTHON_EXE -c "import time; print('Running disabled test...'); time.sleep(3)"
$env:PYNOTIFY_DISABLE = "0"

Write-Host "`n--- TEST 6: Multiprocessing Anti-Spam (Should ONLY ping ONCE) ---" -ForegroundColor Cyan
& $PYTHON_EXE "$PSScriptRoot\test_multiprocessing.py"

Write-Host "`n--- All Tests Complete! ---" -ForegroundColor Green
