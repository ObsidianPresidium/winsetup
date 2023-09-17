@echo off
setlocal enabledelayedexpansion
setlocal enableextensions
set "root=%cd%"
echo Generating locales...

echo --^> Danish
cd locales\da\LC_MESSAGES
python !root!\msgfmt.py -o base.mo base
cd !root!

echo --^> English
cd locales\en\LC_MESSAGES
python !root!\msgfmt.py -o base.mo base
cd !root!

echo.
echo Compiling for .exe
pyinstaller --clean -y --add-data "locales\da\LC_MESSAGES\base.mo;locales\da\LC_MESSAGES" --add-data "locales\en\LC_MESSAGES\base.mo;locales\en\LC_MESSAGES" --onefile main.py

echo.
echo Done^^! .exe should now be at .\dist\main.exe
pause
exit