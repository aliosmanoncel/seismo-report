@echo off
cd /d "%~dp0\.."
python scripts\aftershock_update.py page-update
pause
