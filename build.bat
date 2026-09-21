@echo off
chcp 65001 >nul
echo ========================================
echo Discord BLUE - Build Script
echo ========================================
echo.

echo [1/4] Checking PyInstaller...
python -m pip show pyinstaller
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Error: Cannot install PyInstaller!
        echo Press any key to exit...
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
) else (
    echo PyInstaller is ready.
)
echo.

echo [2/4] Installing required libraries...
echo Installing/Updating Pillow (for avatar support)...
python -m pip install Pillow --quiet
if %errorlevel% neq 0 (
    echo Error: Cannot install Pillow!
    echo Press any key to exit...
    pause
    exit /b 1
)
echo Pillow installed successfully!

echo Installing/Updating requests...
python -m pip install requests --quiet
if %errorlevel% neq 0 (
    echo Error: Cannot install requests!
    echo Press any key to exit...
    pause
    exit /b 1
)
echo requests installed successfully!

echo Installing/Updating pystray (for System Tray feature)...
python -m pip install pystray --quiet
if %errorlevel% neq 0 (
    echo Warning: Cannot install pystray - System Tray feature will be disabled.
) else (
    echo pystray installed successfully!
)

echo All libraries installed!
echo.

echo [3/4] Starting build...
echo Using PyInstaller with "Discord BLUE.spec" (single source of truth)
echo.

python -m PyInstaller --noconfirm --clean "Discord BLUE.spec"

if %errorlevel% neq 0 (
    echo.
    echo Error: Build failed!
    echo Please check the error messages above.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo.
echo [4/4] Build completed!
echo.
echo .exe file created in: dist\
echo.
echo ========================================
echo Press any key to exit...
pause
