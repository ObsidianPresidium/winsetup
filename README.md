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
2. Write translated strings for the different locales in `optu/{locale}`

Use this format when writing a string in optu:

```
"{ID}": ["{ORIGINAL_STRING}", "{TRANSLATED_STRING}"],
```