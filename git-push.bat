@echo off
cd /d "%~dp0"
echo [%date% %time%] GitHub push basliyor...
"C:\Users\oncel\AppData\Local\Python\bin\python.exe" -X utf8 scripts\aftershock_update.py push
echo [%date% %time%] Tamamlandi.
pause
