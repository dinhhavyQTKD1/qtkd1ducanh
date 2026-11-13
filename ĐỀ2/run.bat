@echo off
chcp 65001 >nul
echo ======================================================================
echo    KHỞI CHẠY HỆ THỐNG AI AGENT ĐIỀU PHỐI KHÁCH HÀNG - NAM VIỆT SOFTWARE
echo ======================================================================
call "%~dp0run_python.bat" "%~dp0main.py" %*
echo.
echo Nhấn phím bất kỳ để kết thúc...
pause >nul

