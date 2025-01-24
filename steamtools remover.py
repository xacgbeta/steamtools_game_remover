import os
import subprocess
import re
import sys
import webbrowser
import bs4, requests
from tkinter import *
from tkinter import filedialog
import customtkinter
from threading import Thread
from tkinter.messagebox import askyesno, showinfo

select_steam_path_flg = False
steam_folder = None
steam_stplugin = None
steam_config_depotchache = None
steam_depotchache = None
steam_stui = None
steam_stats = None
files_list = []
flag, ids = False, []


def get_name(game_id):
    try:
        url = f"https://store.steampowered.com/app/{game_id}/"
        response = requests.get(url)
        bs = bs4.BeautifulSoup(response.text, "lxml")
        return bs.find("div", id="appHubAppName").text
    except:
        return "-"


def warning():
    result = showinfo(title="Error", message="Select steam folder!")


def wrong_folder():
    result = showinfo(title="Error", message="Select steam folder!")


def delete_game():
    global entry_id, select_steam_path_flg
    if select_steam_path_flg:
        cnt_files = 0
        while True:
            game_id = entry_id.get()
            if game_id.isdigit():
                files_text.tag_config("yellow", foreground="yellow")
                files_text.tag_config("green", foreground="#5BFF00")
                files_text.tag_config("cyan", foreground="cyan")
                files_text.configure(state="normal")
                files_text.insert(customtkinter.END, f"AppID: {game_id}\nDeleting files:\n", "yellow")
                files_text.configure(state="disabled")
                pattern = rf"{game_id[0:-1]}\d\D+"

                for file in os.listdir(steam_stplugin):                 #st files
                    if re.match(pattern, file):
                        if file != "":
                            # find_dlc(file)
                            files_text.configure(state="normal")
                            files_text.insert(customtkinter.END,
                                              os.path.join(steam_stplugin, file).replace("/", '\\')+"\n", "cyan")
                            os.remove(os.path.join(steam_stplugin, file))
                            files_text.see("end")
                            files_text.configure(state="disabled")
                            cnt_files += 1

                for file1 in os.listdir(steam_depotchache):              #manifests
                    if re.match(pattern, file1):
                        if file1 != "":
                            files_text.configure(state="normal")
                            files_text.insert(customtkinter.END,
                                              os.path.join(steam_depotchache, file1).replace("/", '\\')+"\n", "cyan")
                            os.remove(os.path.join(steam_depotchache, file1))
                            files_text.see("end")
                            files_text.configure(state="disabled")
                            cnt_files += 1

                for file2 in os.listdir(steam_config_depotchache):       #manifests
                    if re.match(pattern, file2):
                        if file2 != "":
                            files_text.configure(state="normal")
                            files_text.insert(customtkinter.END,
                                              os.path.join(steam_config_depotchache, file2).replace("/", '\\')+"\n", "cyan")
                            os.remove(os.path.join(steam_config_depotchache, file2))
                            files_text.see("end")
                            files_text.configure(state="disabled")
                            cnt_files += 1

                for file3 in os.listdir(steam_stats):                  #achieve file
                    if "_"+game_id+"_" in file3:
                        if file3 != "":
                            files_text.configure(state="normal")
                            files_text.insert(customtkinter.END,
                                              os.path.join(steam_stats, file3).replace("/", '\\')+"\n", "cyan")
                            os.remove(os.path.join(steam_stats, file3))
                            files_text.see("end")
                            files_text.configure(state="disabled")
                            cnt_files += 1

                files_text.configure(state="normal")
                if cnt_files != 0:
                    files_text.insert(customtkinter.END, f"\nGame «{get_name(game_id)}» has been removed.\n\n", "green")
                else:
                    files_text.insert(customtkinter.END, f"\nThe AppID: {game_id} files were not found.\n\n", "yellow")
                files_text.see("end")
                files_text.configure(state="disabled")
                break
            else:
                files_text.configure(state="normal")
                files_text.tag_config("red", foreground="red")
                files_text.insert(customtkinter.END, "Invalid ID...\n\n", "red")
                files_text.see("end")
                files_text.configure(state="disabled")
                break
    else:
        warning()


def appear_entry():
    global entry_id
    entry_id = customtkinter.CTkEntry(master=root, placeholder_text="Enter ID", width=107, height=30)
    entry_id.place(x=27, y=136)
    get_id_button = customtkinter.CTkButton(master=root, corner_radius=8, text="Delete", width=60, command=delete_game)
    get_id_button.place(x=137, y=136)


def view_all_games():
    global ids, select_steam_path_flg
    if select_steam_path_flg:
        games_text.configure(state="normal")
        games_text.delete('1.0', 'end')
        games_text.configure(state="disabled")
        cnt = 0
        for file in os.listdir(steam_stplugin):
            if file.endswith("0.st"):
                idgame = file.replace(".st", "")
                cnt += 1
                instext = f"{cnt}. {get_name(idgame)}  AppID: {idgame}\n"
                games_text.configure(state="normal")
                games_text.insert(customtkinter.END, text=instext)
                files_text.see("end")
                games_text.configure(state="disabled")

    else:
        games_text.configure(state="normal")
        games_text.insert(customtkinter.END, "Select Steam folder for view game list")
        games_text.configure(state="disabled")


def total_deleting():
    global paths_for_del
    paths = [steam_stplugin, steam_depotchache, steam_config_depotchache, steam_stats]
    paths_for_del = []
    files_text.configure(state="normal")
    files_text.tag_config("yellow", foreground="yellow")
    files_text.insert(customtkinter.END, "Deletion files...\n", "yellow")
    files_text.configure(state="disabled")
    for path in paths:
        for file in os.listdir(path):
            if file.endswith(".st") or file.endswith(".manifest") or file.endswith(".bin"):
                paths_for_del.append(f'{path}\{file}')
    ask_deletion(paths_for_del)


def ask_deletion(paths_for_del):
    result = askyesno(title="Delete all games?", message="Do you want to delete ALL games?")
    if result:
        confirm_def(paths_for_del)
    else:
        deny_def()


def confirm_def(paths_for_del):
    for file in paths_for_del:
        try:
            files_text.tag_config("cyan", foreground="cyan")
            files_text.tag_config("green", foreground="#5BFF00")
            files_text.configure(state="normal")
            if len(paths_for_del) != 0:
                os.remove(file)
                new_file = file.replace("/", '\\')
                files_text.insert(customtkinter.END, f"{new_file}\n", "cyan")
            else:
                files_text.insert(customtkinter.END, f"1", "green")
                files_text.see("end")
            files_text.configure(state="disabled")
        except Exception as e:
            files_text.configure(state="normal")
            files_text.tag_config("red", foreground="red")
            files_text.insert(customtkinter.END, f"Error deleting {new_file}: {str(e)}\n", "red")
            files_text.configure(state="disabled")
    files_text.configure(state="normal")
    files_text.tag_config("green", foreground="#5BFF00")
    files_text.insert(customtkinter.END, f"The games have been successfully deleted!\n\n", "green")
    files_text.see("end")
    files_text.configure(state="disabled")


def deny_def():
    files_text.configure(state="normal")
    files_text.tag_config("red", foreground="red")
    files_text.insert(customtkinter.END, "File deletion aborted...\n\n", "red")
    files_text.configure(state="disabled")


def delete_steamtools():
    os.system("taskkill /f /im  Steamtools.exe")
    try:
        os.system("taskkill /f /im  Steamtools.exe")
        cnt1 = 0
        files_text.tag_config("green", foreground="#5BFF00")
        files_text.tag_config("yellow", foreground="yellow")
        files_text.tag_config("cyan", foreground="cyan")
        for i in os.listdir(os.path.join(steam_folder, "config", "stUI")):
            cnt1 += 1
        if cnt1 != 0:
            for files in os.listdir(os.path.join(steam_folder, "config", "stUI")):
                os.remove(os.path.join(steam_folder, "config", "stUI", files))
                files_text.configure(state="normal")
                files_text.insert(customtkinter.END, f"Deleted: {os.path.join(steam_folder, 'config', 'stUI', files)}\n", "cyan")
                files_text.configure(state="disabled")
            files_text.configure(state="normal")
            files_text.insert(customtkinter.END, f"The Steamtools have been successfully deleted!\n\n", "green")
            files_text.configure(state="disabled")
        else:
            files_text.configure(state="normal")
            files_text.insert(customtkinter.END, f"Steamtools has already been deleted.\n\n", "yellow")
            files_text.configure(state="disabled")
            files_text.see("end")
    except Exception as e:
        files_text.configure(state="normal")
        files_text.tag_config("red", foreground="red")
        files_text.insert(customtkinter.END, f"Steamtools has already been deleted.\n\n", "yellow")
        files_text.configure(state="disabled")
        files_text.see("end")


def ask_deletion_steamtools():
    files_text.tag_config("red", foreground="red")
    files_text.tag_config("yellow", foreground="yellow")
    files_text.configure(state="normal")
    files_text.insert(customtkinter.END, f"Delete Steamtools?\n", "yellow")
    result = askyesno(title="Delete Steamtools?", message="Do you want to delete Steamtools?")
    files_text.configure(state="disabled")
    if result:
        delete_steamtools()
    else:
        files_text.configure(state="normal")
        files_text.insert(customtkinter.END, f"Steamtools deletion aborted...\n\n", "red")
        files_text.configure(state="disabled")


def browse():
    global folder_selected, steam_folder, select_steam_path_flg, steam_stui, steam_depotchache, steam_config_depotchache, steam_stats, steam_stplugin
    root1 = Tk()
    root1.withdraw()
    folder_selected = filedialog.askdirectory()
    fold = []
    for folders in os.listdir(folder_selected):
        fold.append(folders)
    if "config" in fold:
        root1.destroy()
        entry_path.configure(state="normal")
        entry_path.delete(0, "end")
        entry_path.insert("1", folder_selected)
        entry_path.configure(state="disabled")
        select_steam_path_flg = True
        steam_folder = folder_selected
        steam_stplugin = steam_folder+"\config\stplug-in"
        steam_config_depotchache = steam_folder+"\config\depotcache"
        steam_depotchache = steam_folder+"\depotcache"
        steam_stui = steam_folder+"\config\stUI"
        steam_stats = steam_folder+"\config\StatsExport"
        threading()
    else:
        wrong_folder()


def restart_steam():
    steam_exe = "Steam.exe"
    steam_path = os.path.join(steam_folder, steam_exe)
    files_text.configure(state="normal")
    files_text.tag_config("green", foreground="#5BFF00")
    files_text.tag_config("yellow", foreground="yellow")
    files_text.tag_config("red", foreground="red")
    files_text.insert(customtkinter.END, "Restarting Steam\n\n", "yellow")
    files_text.configure(state="disable")
    try:
        subprocess.run(["taskkill", "/f", "/im", steam_exe], check=True)
    except:
        pass
    try:
        files_text.configure(state="normal")
        if os.path.exists(steam_path):
            subprocess.Popen(steam_path, shell=True)
            files_text.insert(customtkinter.END, "Steam has been restarted.\n\n", "green")
        else:
            files_text.insert(customtkinter.END, "Steam.exe not found in the selected folder.\n", "red")
    except subprocess.CalledProcessError as e:
        files_text.configure(state="normal")
        files_text.insert(customtkinter.END, f"Error restarting Steam: {str(e)}\n", "red")
    except Exception as e:
        files_text.configure(state="normal")
        files_text.insert(customtkinter.END, f"Unexpected error: {str(e)}\n", "red")
    finally:
        files_text.configure(state="disabled")


def threading():
    thread = Thread(target=view_all_games)
    games_text.configure(state="normal")
    games_text.delete('1.0', 'end')
    thread.start()


def exit_str():
    root.destroy()
    sys.exit()


root = customtkinter.CTk()
root.title("Steamtools remover")
root.geometry(f"{1200}x{600}")
root.resizable(False, False)

c = Canvas(root, width=2000, height=1000, bg="#242424", borderwidth=0, highlightthickness=0)
c.place(x=0, y=0)

select_text = c.create_text(120, 33, text="Select Steam folder", fill="white", font=("Helvetica", 13))
select_top1_border = c.create_line(20, 35, 40, 35, width=1, fill="#565B5E")
select_top2_border = c.create_line(200, 35, 724, 35, width=1, fill="#565B5E")
select_left_border = c.create_line(20, 35, 20, 97, width=1, fill="#565B5E")
select_right_border = c.create_line(724, 35, 724, 97, width=1, fill="#565B5E")
select_bottom_border = c.create_line(20, 97, 724, 97, width=1, fill="#565B5E")
browse_button = customtkinter.CTkButton(master=root, text="...", corner_radius=8, width=40, command=browse)

entry_path = customtkinter.CTkEntry(master=root, placeholder_text="Enter the path "+"-"*120+">", width=495, height=30)
entry_path.place(y=40, x=25)
entry_path.configure(state="disabled")
browse_button.place(y=40, x=530)

delete_button = customtkinter.CTkButton(master=root, text="Delete a SteamTools game",
                                        corner_radius=8, command=appear_entry, width=140)
delete_button.place(x=27, y=100)
delete_all_button = customtkinter.CTkButton(master=root, text="Delete ALL SteamTools game",
                                            corner_radius=8, command=total_deleting, width=190)
delete_all_button.place(x=220, y=100)
delete_steamtools_button = customtkinter.CTkButton(master=root, text="Delete SteamTools",
                                                   corner_radius=8, command=ask_deletion_steamtools, width=190)
delete_steamtools_button.place(x=220, y=136)
channel_button = customtkinter.CTkButton(master=root, text="Channel with games",
                                                   corner_radius=8, command=lambda: webbrowser.open('https://t.me/MACTEP_CBO_ZOV'), width=140)
channel_button.place(x=430, y=100)
entry_id = None
options_text = c.create_text(75, 110, text="Options", fill="white", font=("Helvetica", 13))
options_top1_border = c.create_line(20, 110, 40, 110, width=1, fill="#565B5E")
options_top2_border = c.create_line(110, 110, 724, 110, width=1, fill="#565B5E")
options_left_border = c.create_line(20, 110, 20, 222, width=1, fill="#565B5E")
options_right_border = c.create_line(724, 110, 724, 222, width=1, fill="#565B5E")
options_bottom_border = c.create_line(20, 222, 724, 222, width=1, fill="#565B5E")
options_mid1_border = c.create_line(260, 110, 260, 222, width=1, fill="#565B5E")
options_mid2_border = c.create_line(527, 110, 527, 222, width=1, fill="#565B5E")
# 3
steamtools_games = c.create_text(113, 240, text="SteamTools games", fill="white", font=("Helvetica", 13))
games_text = customtkinter.CTkTextbox(master=root, width=544, height=330)
games_text.place(y=205, x=26)
st_games_top1_border = c.create_line(20, 240, 40, 240, width=1, fill="#565B5E")
st_games_top2_border = c.create_line(188, 240, 724, 240, width=1, fill="#565B5E")
st_games_left_border = c.create_line(20, 240, 20, 680, width=1, fill="#565B5E")
st_games_right_border = c.create_line(724, 240, 724, 680, width=1, fill="#565B5E")
st_games_bottom_border = c.create_line(20, 680, 724, 680, width=1, fill="#565B5E")
refresh_button = customtkinter.CTkButton(master=root, text="Refresh", corner_radius=8, width=100, command=threading)
refresh_button.place(x=20, y=560)
# 4
progress = c.create_text(810, 33, text="Progress", fill="white", font=("Helvetica", 13))
files_text = customtkinter.CTkTextbox(master=root, width=560, height=493)
files_text.place(y=40, x=610)
files_text.configure(state="disabled")
progress_left_border = c.create_line(750, 35, 750, 680, width=1, fill="#565B5E")
progress_top1_border = c.create_line(750, 35, 770, 35, width=1, fill="#565B5E")
progress_top2_border = c.create_line(850, 35, 1480, 35, width=1, fill="#565B5E")
progress_right_border = c.create_line(1480, 35, 1480, 680, width=1, fill="#565B5E")
progress_bottom_border = c.create_line(750, 680, 1480, 680, width=1, fill="#565B5E")
# 5
exit_button = customtkinter.CTkButton(master=root, text="Exit", corner_radius=8, width=100, command=exit_str)
exit_button.place(x=1080, y=560)
restart_button = customtkinter.CTkButton(master=root, text="Restart Steam", corner_radius=8,
                                         width=100, command=lambda: restart_steam())
restart_button.place(x=960, y=560)

thread = Thread(target=view_all_games)
thread.start()
root.mainloop()