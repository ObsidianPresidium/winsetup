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
from threading import Timer

pyversion = "3.11"

apps = [
    # name in GUI, winget package name, checked or not (1 or 0)
    ["Chrome", "Google.Chrome", 0],
    ["Firefox", "Mozilla.Firefox", 1],
    ["7-Zip", "7zip.7zip", 1],
    ["Authy", "Twilio.Authy", 1],
    ["Notepad++", "Notepad++.Notepad++", 1],
    ["GNU Nano", "GNU.Nano", 1],
    ["Python 3.11", "Python.Python.3.11", 1],
    ["Modern Powershell", "Microsoft.Powershell", 1],
    ["Visual Studio Code", "Microsoft.VisualStudioCode", 1],
    ["Simplenote", "Automattic.Simplenote", 1],
    ["Adobe Acrobat Reader DC", "Adobe.Acrobat.Reader.64-bit", 0]
]

default_widgets = []
winsetup_dir = os.getenv("APPDATA") + "\\winsetup"
windll = ctypes.windll.kernel32
iso_language = locale.windows_locale[windll.GetUserDefaultUILanguage()]

if "da" in iso_language:
    language = Optu("da")
    _ = language.get_string
else:
    language = Optu()
    _ = language.get_string

alias_select_file_options = [_("New Alias")]

toggles = {
    "cmd_hotkey": os.path.exists(os.getenv("USERPROFILE") + "\\Desktop\\cmd.lnk")
}

main_window = tk.Tk()
padx = 8
pady = 4
current_row = 0


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


is_admin = is_admin()
title = f"ADMIN: {_('Winsetup Script')}" if is_admin else _("Winsetup Script")
main_window.title(title)


def as_admin(exe, args=None):
    if not args:
        if " " in exe:
            args = exe.split(" ")
            exe = args[0]
            args = args.pop(0)
            args = " ".join(args)
        else:
            args = ""
    if is_admin:
        os.system(exe + " " + args)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, args, None, 1)


def create_hotkey(target, shortcut_name, hotkey, start_in=None, remove=False):
    shortcut_script = [
        "Set oWS = WScript.CreateObject(\"WScript.Shell\")\n",
        f"sLinkFile = \"{os.getenv('USERPROFILE')}\\Desktop\\{shortcut_name}.lnk\"\n",
        "Set oLink = oWS.CreateShortcut(sLinkFile)\n",
        f"oLink.TargetPath = \"{target}\"\n",
    ]
    if start_in:
        shortcut_script += [f"oLink.WorkingDirectory = \"{start_in}\"\n"]

    shortcut_script += [f"oLink.Hotkey = \"{hotkey}\"\n", "oLink.Save()"]
    script_location = f"{os.getenv('TEMP')}/tempscript_{shortcut_name}.vbs"
    with open(script_location, "w") as file:
        file.writelines(shortcut_script)

    os.system(script_location)
    os.remove(script_location)
    os.system(f"attrib +H \"{os.getenv('USERPROFILE')}\\Desktop\\{shortcut_name}.lnk\"")

def create_cmd_hotkey():
    global create_cmd_hotkey_button
    if not toggles["cmd_hotkey"]:
        create_hotkey("C:\\Windows\\System32\\cmd.exe", "cmd", "Ctrl+alt+t", os.getenv("USERPROFILE"))
        create_cmd_hotkey_button.configure(text=_("Disable keyboard shortcut for the command prompt"))
        toggles["cmd_hotkey"] = True
    else:
        os.remove(os.getenv("USERPROFILE") + "\\Desktop\\cmd.lnk")
        create_cmd_hotkey_button.configure(text=_("Enable keyboard shortcut for the command prompt"))
        toggles["cmd_hotkey"] = False


def set_registry_keys(os_version):
    # Disable wallpaper compression
    as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Control Panel\\Desktop\" /f /v JPEGImportQuality /t REG_DWORD /d 100")  # value doesn't exist by default

    # Show file extensions
    as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\" /f /v HideFileExt /t REG_DWORD /d 0")  # default 1

    if os_version == 11:
        # Enable compact mode in explorer
        as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\" /f /v UseCompactMode /t REG_DWORD /d 1")  # default 0

        # Enable legacy context menu
        as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32\" /f /ve")  # value doesn't exist by default

        # Disable Bing in start menu
        as_admin("C:/Windows/System32/reg.exe", "add \"HKCU\\Software\\Policies\\Microsoft\\Windows\\Explorer\" /f /v DisableSearchBoxSuggestions /t REG_DWORD /d 1")  #


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


def open_users_dialog():
    as_admin("netplwiz")


def check_winget():
    return os.path.exists(f"{os.getenv('LOCALAPPDATA')}/Microsoft/WindowsApps/winget.exe")


def install_winget():
    if not check_winget():
        subprocess.run(["powershell", "-Command", "Start-Process ms-appinstaller:?source=https://aka.ms/getwinget"])
        while not check_winget():
            time.sleep(1)
    else:
        tkmsg.showinfo(_("Winsetup Script"), _("Winget is already installed."))

    return 0


def install_wsl():
    subprocess.Popen(["powershell", "wsl", "--install"])


def relaunch_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    exit(0)


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


def ensure_winsetup_dir():
    if not os.path.exists(winsetup_dir):
        os.mkdir(winsetup_dir)
    if not os.path.exists(winsetup_dir + "\\aliases"):
        os.mkdir(winsetup_dir + "\\aliases")

    if not "winsetup" in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + os.path.join(winsetup_dir, "aliases")
        os.system(f"powershell setx PATH ((Get-ItemProperty HKCU:\\Environment).PATH + ';{winsetup_dir}\\aliases')")


def alias_status_message(message, status_label):
    def subroutine(message, status_label):
        if status_label.cget("text") == message:
            status_label.config(text = "")
    timer = Timer(3.0, subroutine, (message, status_label))
    status_label.config(text = message)
    timer.start()


def create_alias(text_widget, file_name, status_label):
    ensure_winsetup_dir()

    if os.path.exists(winsetup_dir + f"\\aliases\\{file_name.get()}.bat"):
        answer = tkmsg.askyesno(_("Winsetup Script"), _("There already exists an alias with the name '%s'.\nAre you sure you want to replace it?", f=[file_name.get()]))
        if not answer:
            alias_status_message(_("Alias was not replaced"), status_label)
            return 0
    if file_name.get() == "":
        alias_status_message(_("Alias name cannot be empty"), status_label)
    else:
        lines = text_widget.get("1.0", "end-1c")
        lines = lines.split("\n")
        lines.insert(0, "@echo off")
        for line in enumerate(lines):
            lines[line[0]] = line[1] + "\n"
        with open(winsetup_dir + f"\\aliases\\{file_name.get()}.bat", "w") as file:
            file.writelines(lines)
            alias_status_message(_("Success! Alias '%s' was written", f=[file_name.get()]), status_label)

        update_file_selector(file_name.get())

def delete_alias(file_name, status_label):
    ensure_winsetup_dir()
    alias_path = winsetup_dir + f"\\aliases\\{file_name.get()}.bat"
    if os.path.exists(alias_path):
        answer = tkmsg.askyesno(_("Winsetup Script"), _("Are you sure you want to permanently delete this alias?"))
        if answer:
            os.remove(alias_path)
            alias_status_message(_("Alias was deleted"), status_label)
            update_file_selector(_("New Alias"))
    else:
        alias_status_message(_("Could not find alias"), status_label)

def alias_get_files():
    ensure_winsetup_dir()
    mylist = os.listdir(winsetup_dir + f"\\aliases\\")
    for file in enumerate(mylist):
        mylist[file[0]] = file[1].replace(".bat", "")
    return mylist


def alias_get_file(selected_file, file_name, text_area, status_log):
    if not type(selected_file) == str:
        selected_file = selected_file.get()
    if selected_file == _("New Alias"):
        file_name.set("")
        alias_status_message(_("Editing new alias"), status_log)
    else:
        with open(f"{winsetup_dir}\\aliases\\{selected_file}.bat") as file:
            lines = file.readlines()
        string = ""
        for line in enumerate(lines):
            if line[0] > 0:
                string += line[1]
        string = string[0:-1]
        text_area.delete("1.0", "end")
        text_area.insert("1.0", string)
        file_name.set(selected_file)
        alias_status_message(_("Opened alias %s", f=[selected_file]), status_log)


def update_file_selector(new_selected):
    global alias_existing_aliases
    global alias_select_file_options
    global alias_selected_file
    del alias_existing_aliases
    alias_select_file_options = [_("New Alias")] + alias_get_files()
    alias_selected_file.set(new_selected)
    alias_existing_aliases = tk.OptionMenu(alias_top_frame, alias_selected_file, *alias_select_file_options, command=lambda x: alias_get_file(alias_selected_file, alias_file_name, alias_create_alias_text, alias_status_label))
    alias_existing_aliases.grid(sticky="e", row=0, column=1, padx=padx, pady=pady)



# GUI
running_win_11 = tk.IntVar(value=1 if sys.getwindowsversion().build >= 22000 else 0)
alias_file_name = tk.StringVar()
alias_selected_file = tk.StringVar()

default_container_frame = tk.Frame(main_window)
default_container_frame.grid(row=0, padx=padx, pady=pady)
# default_container_frame.pack(fill="both", expand=True, padx=padx, pady=pady)

create_cmd_hotkey_button = tk.Button(default_container_frame, text=_("Disable keyboard shortcut for the command prompt") if toggles["cmd_hotkey"] else _("Enable keyboard shortcut for the command prompt"), command=create_cmd_hotkey)
create_cmd_hotkey_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

set_registry_keys_button = tk.Button(default_container_frame, text=_("Setup various registry keys"), command=lambda: set_registry_keys(11 if running_win_11.get() == 1 else 10))
set_registry_keys_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
set_registry_keys_tooltip = Hovertip(set_registry_keys_button, _(6))
set_registry_keys_checkbox = tk.Checkbutton(default_container_frame, text=_("I'm running Windows 11"), variable=running_win_11, onvalue=1, offvalue=0)
set_registry_keys_checkbox.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

restart_explorer_button = tk.Button(default_container_frame, text=_("Restart explorer.exe"), command=lambda: restart_explorer(main_window))
restart_explorer_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

open_uac_button = tk.Button(default_container_frame, text=_("Open the UAC control panel"), command=open_uac)
open_uac_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

open_display_settings_button = tk.Button(default_container_frame, text=_("Open display settings"), command=open_display_settings)
open_display_settings_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

open_users_dialog_button = tk.Button(default_container_frame, text=_("Open Users dialog"), command=open_users_dialog)
open_users_dialog_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)

install_winget_button = tk.Button(default_container_frame, text=_("Install Winget"), command=install_winget)
install_winget_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
install_winget_tooltip = Hovertip(install_winget_button, _("Checks if winget is installed, and if not, this opens a window, which lets you install it."))

install_wsl_button = tk.Button(default_container_frame, text=_("Install WSL"), command=install_wsl)
install_wsl_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
install_wsl_tooltip = Hovertip(install_wsl_button, _("Installs Windows Subsystem for Linux with the default distro, Ubuntu LTS"))

relaunch_as_admin_button = tk.Button(default_container_frame, text=_("Relaunch as administrator"), command=relaunch_as_admin)
relaunch_as_admin_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
relaunch_as_admin_tooltip = Hovertip(relaunch_as_admin_button, _("Relaunches winsetup as administrator, suppressing additional UAC prompts."))

switch_scene_alias_button = tk.Button(default_container_frame, text=_("Create Command Alias"), command=lambda: set_scene("alias"))
switch_scene_alias_button.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
switch_scene_alias_tooltip = Hovertip(switch_scene_alias_button, _("A wizard which lets you create aliases on the command-line."))

color_mode_frame = tk.LabelFrame(default_container_frame, text=_("Color mode"))
color_mode_frame.grid(sticky="w", row=get_row(), padx=padx, pady=pady)
color_mode_integer_desktop = tk.IntVar(value=1)
color_mode_checkbox_desktop = tk.Checkbutton(color_mode_frame, text=_("Enable dark mode for the desktop"), variable=color_mode_integer_desktop, onvalue=1, offvalue=0)
color_mode_checkbox_desktop.grid(sticky="w", row=0, padx=padx, pady=pady)
color_mode_integer_apps = tk.IntVar(value=0)
color_mode_checkbox_apps = tk.Checkbutton(color_mode_frame, text=_("Enable dark mode for applications"), variable=color_mode_integer_apps, onvalue=1, offvalue=0)
color_mode_checkbox_apps.grid(sticky="w", row=1, padx=padx, pady=pady)
color_mode_apply_button = tk.Button(color_mode_frame, text=_("Apply this color mode"), command=lambda: set_color_mode(color_mode_integer_desktop, color_mode_integer_apps))
color_mode_apply_button.grid(row=2, padx=padx, pady=pady)

apps_frame = tk.LabelFrame(default_container_frame, text=_("Applications"))
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
additional_packages_area.grid(sticky="w", row=row_after_apps + 1, padx=padx, pady=pady)

apps_install_button = tk.Button(apps_frame, text=_("Install applications"), command=lambda: install_apps(interpret_apps_checkboxes(apps_gui_widgets), additional_packages_area))
apps_install_button.grid(row=row_after_apps + 2, padx=padx, pady=pady)

default_widgets = default_container_frame.winfo_children().copy()

alias_select_file_options += alias_get_files()
alias_selected_file.set(_("New Alias"))

alias_container_frame = tk.LabelFrame(main_window, text=_("Create Alias"))
alias_top_frame = tk.Frame(alias_container_frame)
alias_top_frame.grid(sticky="w", padx=padx, pady=pady)
alias_file_name_entry = tk.Entry(textvariable=alias_file_name, master=alias_top_frame)
alias_file_name_entry.grid(sticky="w", row=0, column=0, padx=padx, pady=pady)
alias_existing_aliases = tk.OptionMenu(alias_top_frame, alias_selected_file, *alias_select_file_options, command=lambda x: alias_get_file(alias_selected_file, alias_file_name, alias_create_alias_text, alias_status_label))
alias_existing_aliases.grid(sticky="e", row=0, column=1, padx=padx, pady=pady)

alias_middle_frame = tk.Frame(alias_container_frame)
alias_middle_frame.grid(row=1, padx=padx, pady=pady)
alias_create_alias_text = tk.Text(alias_middle_frame, width=30, height=10)
alias_create_alias_text.grid(row=0, padx=padx, pady=pady)
alias_status_label = tk.Label(alias_middle_frame, text="", width=20)
alias_status_label.grid(row=0, column=1, padx=padx, pady=pady)

alias_bottom_frame = tk.Frame(alias_container_frame)
alias_bottom_frame.grid(sticky="e", row=2, padx=padx, pady=pady)
alias_back_button = tk.Button(alias_bottom_frame, text=_("Back"), command=lambda: set_scene("default"))
alias_back_button.grid(row=3, padx=padx, pady=pady)
alias_delete_button = tk.Button(alias_bottom_frame, text=_("Delete"), command=lambda: delete_alias(alias_file_name, alias_status_label))
alias_delete_button.grid(row=3, column=1, padx=padx, pady=pady)
alias_create_alias_button = tk.Button(alias_bottom_frame, text=_("Save Alias to Path"), command=lambda: create_alias(alias_create_alias_text, alias_file_name, alias_status_label))
alias_create_alias_button.grid(row=3, column=2, padx=padx, pady=pady)


def set_scene(scene_name="default"):
    if scene_name == "default":
        alias_container_frame.grid_remove()
        default_container_frame.grid()
    if scene_name == "alias":
        default_container_frame.grid_remove()
        alias_container_frame.grid(row=0, padx=padx, pady=pady)


if __name__ == "__main__":
    main_window.mainloop()
