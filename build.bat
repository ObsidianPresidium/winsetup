@echo off
setlocal enabledelayedexpansion
setlocal enableextensions
set "root=%cd%"

echo.
echo Compiling for .exe
pyinstaller --clean -y --add-data "optu\da\main.json;optu\da" --add-data "optu\en\main.json;optu\en" --onefile main.py

echo.
echo Done^^! .exe should now be at .\dist\main.exe
pause
exit