@echo off
setlocal

:: 1. Uu tien dung Python cua MySQL Workbench (Moi truong san co tren may)
if exist "C:\Program Files\MySQL\MySQL Workbench 8.0\python.exe" (
    set "PYTHONHOME=C:\Program Files\MySQL\MySQL Workbench 8.0\python"
    set "PYTHONPATH=%~dp0;%PYTHONHOME%\lib;%PYTHONHOME%\site-packages"
    "C:\Program Files\MySQL\MySQL Workbench 8.0\python.exe" -u %*
    exit /b %errorlevel%
)

:: 2. Kiem tra neu python co san trong PATH he thong
where python.exe >nul 2>&1
if %errorlevel% equ 0 (
    python.exe -u %*
    exit /b %errorlevel%
)

:: 3. Kiem tra Python Launcher (py.exe)
where py.exe >nul 2>&1
if %errorlevel% equ 0 (
    py.exe -3 -u %*
    exit /b %errorlevel%
)

:: 4. Kiem tra cac duong dan cai dat Python pho bien tren Windows
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -u %*
    exit /b %errorlevel%
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -u %*
    exit /b %errorlevel%
)
if exist "C:\Python312\python.exe" (
    "C:\Python312\python.exe" -u %*
    exit /b %errorlevel%
)
if exist "C:\Python311\python.exe" (
    "C:\Python311\python.exe" -u %*
    exit /b %errorlevel%
)

echo [ERROR] Khong tim thay moi truong Python tren may tinh nay.
echo Vui long cai dat Python 3.10+ tu https://www.python.org de khoi chay Nam Viet AI Agent.
exit /b 1
