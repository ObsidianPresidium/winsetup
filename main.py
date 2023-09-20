import os
import ctypes
import sys
import subprocess
import time
import tkinter as tk
import tkinter.messagebox as tkmsg
from idlelib.tooltip import Hovertip
from optu import Optu
import locale

pyversion = "3.11"

apps = [
    # name in GUI, winget package name, checked or not (1 or 0)
    ["Chrome", "Google.Chrome", 0],
    ["Firefox", "Mozilla.Firefox", 1],
    ["7-Zip", "7zip.7zip", 1],
    ["Authy", "Twilio.Authy", 1],
    ["Notepad++", "Notepad++.Notepad++", 1],
    ["Python 3.11", "Python.Python.3.11", 1],
    ["Simplenote", "Automattic.Simplenote", 1],
    ["Visual Studio Code", "Microsoft.VisualStudioCode", 1],
    ["Adobe Acrobat Reader DC", "Adobe.Acrobat.Reader.64-bit", 0]
]

windll = ctypes.windll.kernel32
iso_language = locale.windows_locale[windll.GetUserDefaultUILanguage()]

if "da" in iso_language:
    language = Optu("da")
    _ = language.get_string
else:
    language = Optu()
    _ = language.get_string

main_window = tk.Tk()
main_window.title(_("Winsetup Script"))
padx = 8
pady = 4
current_row = 0


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


is_admin = is_admin()


def as_admin(exe, args=None):
    if not args:
        if " " in exe:
            args = exe.split(" ")
            exe = args[0]
            args = args.pop(0)
            args = " ".join(args)
        else:
            args = ""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, args, None, 1)


def create_cmd_hotkey():
    shortcut_script = [
        "Set oWS = WScript.CreateObject(\"WScript.Shell\")\n",
        f"sLinkFile = \"{os.getenv('USERPROFILE')}\\Desktop\\cmd.lnk\"\n",
        "Set oLink = oWS.CreateShortcut(sLinkFile)\n",
        "oLink.TargetPath = \"C:\\Windows\\System32\\cmd.exe\"\n",
        "oLink.Hotkey = \"Ctrl+Alt+t\"\n",
        "oLink.Save()"
    ]
    script_location = f"{os.getenv('TEMP')}/create_cmd_hotkey.vbs"
    with open(script_location, "w") as file:
        file.writelines(shortcut_script)

    os.system(script_location)


def set_registry_keys(os_version):
    # Disable wallpaper compression
    as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Control Panel\\Desktop\" /f /v JPEGImportQuality /t REG_DWORD /d 100")

    if os_version == 11:
        # Enable compact mode in explorer
        as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\" /f /v UseCompactMode /t REG_DWORD /d 1")

        # Enable legacy context menu
        as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32\" /f /ve")


def restart_explorer(tkwindow):
    answer = tkmsg.askyesno(title=_("Restart explorer.exe"), parent=tkwindow, message=_("Are you sure you want to restart explorer.exe?\nRestarting explorer.exe will close all open explorer windows."))
    if not answer:
        return 0

    os.system("taskkill /f /im explorer.exe")
    subprocess.Popen(["C:/Windows/explorer.exe"])

def open_uac():
    subprocess.Popen(["C:/Windows/System32/UserAccountControlSettings.exe"])


def open_display_settings():
    subprocess.Popen(["powershell", "Start-Process", "ms-settings:display"])


def check_winget():
    return os.path.exists(f"{os.getenv('LOCALAPPDATA')}/Microsoft/WindowsApps/winget.exe")


def install_winget():
    if not check_winget():
        subprocess.run(["powershell", "-Command", "Start-Process ms-appinstaller:?source=https://aka.ms/getwinget"])
        while not check_winget():
            time.sleep(1)
    else:
        print(_("Winget is already installed."))

    return 0


def install_wsl():
    subprocess.Popen(["powershell", "wsl", "--install"])

def get_row():
    global current_row
    current_row += 1
    return current_row - 1


def set_color_mode(desktop, apps):
    as_admin("C:/Windows/System32/reg.exe", f"add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /f /v SystemUsesLightTheme /t REG_DWORD /d {0 if desktop.get() == 1 else 1}")
    as_admin(f"C:/Windows/System32/reg.exe", f"add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /f /v AppsUseLightTheme /t REG_DWORD /d {0 if apps.get() == 1 else 1}")


def install_apps(apps_to_install, textarea):
    if check_winget():
        textarea_value = textarea.get("1.0", "end-1c")
        if not textarea_value == "":
            apps_to_install += textarea_value.split("\n")

        installation_string = ""
        for i in apps_to_install:
            installation_string += f"winget install {i}; "

        os.system(f'start powershell {installation_string[:-2]}')


def interpret_apps_checkboxes(widgets):
    final_list = []
    for i in widgets:
        if i[1].get() == 1:  # if checked state is checked
            final_list.append(apps[i[2]][1])  # append to final list: internal id of widget in apps, and get the package name
    return final_list


# GUI
running_win_11 = tk.IntVar(value=1 if sys.getwindowsversion().build >= 22000 else 0)

container_frame = tk.Frame(main_window)
container_frame.grid(row=0, padx=padx, pady=pady)
container_frame.pack(fill="both", expand=True, padx=padx, pady=pady)

create_cmd_hotkey_button = tk.Button(container_frame, text=_("Enable keyboard shortcut for the command prompt"), command=create_cmd_hotkey)
create_cmd_hotkey_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

set_registry_keys_button = tk.Button(container_frame, text=_("Setup various registry keys"), command=lambda: set_registry_keys(11 if running_win_11.get() == 1 else 10))
set_registry_keys_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
set_registry_keys_tooltip = Hovertip(set_registry_keys_button, _("Disables wallpaper JPEG compression\nIf 'I'm running Windows 11' is checked, this will enable compact mode in Explorer, and the legacy context menu."))
set_registry_keys_checkbox = tk.Checkbutton(container_frame, text=_("I'm running Windows 11"), variable=running_win_11, onvalue=1, offvalue=0)
set_registry_keys_checkbox.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

restart_explorer_button = tk.Button(container_frame, text=_("Restart explorer.exe"), command=lambda: restart_explorer(main_window))
restart_explorer_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

open_uac_button = tk.Button(container_frame, text=_("Open the UAC control panel"), command=open_uac)
open_uac_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

open_display_settings_button = tk.Button(container_frame, text=_("Open display settings"), command=open_display_settings)
open_display_settings_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

install_winget_button = tk.Button(container_frame, text=_("Install Winget"), command=install_winget)
install_winget_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
install_winget_tooltip = Hovertip(install_winget_button, _("Checks if winget is installed, and if not, this opens a window, which lets you install it."))

install_wsl_button = tk.Button(container_frame, text=_("Install WSL"), command=install_wsl)
install_wsl_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
install_wsl_tooltip = Hovertip(install_wsl_button, _("Installs Windows Subsystem for Linux with the default distro, Ubuntu LTS"))

color_mode_frame = tk.LabelFrame(container_frame, text=_("Color mode"))
color_mode_frame.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
color_mode_integer_desktop = tk.IntVar(value=1)
color_mode_checkbox_desktop = tk.Checkbutton(color_mode_frame, text=_("Enable dark mode for the desktop"), variable=color_mode_integer_desktop, onvalue=1, offvalue=0)
color_mode_checkbox_desktop.grid(sticky="w", row=0, padx=padx, pady=pady)
color_mode_integer_apps = tk.IntVar(value=0)
color_mode_checkbox_apps = tk.Checkbutton(color_mode_frame, text=_("Enable dark mode for applications"), variable=color_mode_integer_apps, onvalue=1, offvalue=0)
color_mode_checkbox_apps.grid(sticky="w", row=1, padx=padx, pady=pady)
color_mode_apply_button = tk.Button(color_mode_frame, text=_("Apply this color mode"), command=lambda: set_color_mode(color_mode_integer_desktop, color_mode_integer_apps))
color_mode_apply_button.grid(row=2, padx=padx, pady=pady)


apps_frame = tk.LabelFrame(container_frame, text=_("Applications"))
apps_frame.grid(sticky="e", row=0, rowspan=999, column=1, padx=padx, pady=pady)

apps_gui_widgets = []

for i in enumerate(apps):
    checked_state = tk.IntVar(value=i[1][2])
    internal_id = i[0]
    widget = tk.Checkbutton(apps_frame, text=i[1][0], variable=checked_state, onvalue=1, offvalue=0)
    widget.grid(sticky="w", row=i[0], padx=padx, pady=pady)
    apps_gui_widgets.append([widget, checked_state, internal_id])

row_after_apps = len(apps_gui_widgets)

additional_packages_label = tk.Label(apps_frame, text=_("Additional Packages"))
additional_packages_label.grid(row=row_after_apps, padx=padx, pady=pady)
additional_packages_area = tk.Text(apps_frame, height=5, width=30, wrap="none")
additional_packages_area.grid(sticky="w", row=row_after_apps+1, padx=padx, pady=pady)

apps_install_button = tk.Button(apps_frame, text=_("Install applications"), command=lambda: install_apps(interpret_apps_checkboxes(apps_gui_widgets), additional_packages_area))
apps_install_button.grid(row=row_after_apps+2, padx=padx, pady=pady)


if __name__ == "__main__":
    main_window.mainloop()
