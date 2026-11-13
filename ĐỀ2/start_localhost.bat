@echo off
chcp 65001 >nul
echo ======================================================================
echo    KHỞI ĐỘNG MÁY CHỦ AI AGENT LOCALHOST - CÔNG TY PHẦN MỀM NAM VIỆT
echo ======================================================================
echo Mở trình duyệt web (Chrome, Edge, Firefox) và truy cập:
echo.
echo    http://localhost:8000
echo.
echo ======================================================================
call "%~dp0run_python.bat" "%~dp0server.py"
pause

