# winsetup

A Python script for Windows 10 and up that applies my preferred customizations.

## How to build winsetup

1. Install `pyinstaller`.
2. Clone the repository.
`git clone https://github.com/ObsidianPresidium/winsetup.git`
3. Run `build.bat` which should be inside of the newly cloned repository.
4. The compiled exe should be at `winsetup\dist\main.exe`.

## How to add more strings to the script

1. Write the string. Remember to use gettext format `_("{STRING}")`
2. Use a pygettext.py script in winsetups root with these arguments `py pygettext.py -d base -o locales/base.pot main.py`
3. Copy differences between output base.pot and locales/en/LC_MESSAGES/base.po into base.po.
4. Remember to translate into other languages.