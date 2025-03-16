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

# Global variables
steam_folder = None
steam_paths = {
    "stplugin": None,
    "config_depotcache": None,
    "depotcache": None, 
    "stui": None,
    "stats": None
}
select_steam_path_flg = False


def get_game_name(game_id):
    try:
        url = f"https://store.steampowered.com/app/{game_id}/"
        response = requests.get(url)
        bs = bs4.BeautifulSoup(response.text, "lxml")
        return bs.find("div", id="appHubAppName").text
    except:
        return "-"


def show_message(title, message):
    showinfo(title=title, message=message)


def update_log(text, color="white"):
    files_text.configure(state="normal")
    files_text.tag_config(color, foreground=color)
    files_text.insert(customtkinter.END, text, color)
    files_text.see("end")
    files_text.configure(state="disabled")


def delete_game():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    game_id = entry_id.get()
    if not game_id.isdigit():
        update_log("Invalid ID...\n\n", "red")
        return
        
    file_count = 0
    game_name = get_game_name(game_id)
    update_log(f"AppID: {game_id}\nDeleting files:\n", "yellow")
    pattern = rf"{game_id[0:-1]}\d\D+"
    
    for path_key, path in steam_paths.items():
        if path is None:
            continue
            
        for file in os.listdir(path):
            if path_key == "stats":
                match = f"_{game_id}_" in file
            else:
                match = re.match(pattern, file)
                
            if match and file:
                try:
                    full_path = os.path.join(path, file).replace("/", '\\')
                    update_log(f"{full_path}\n", "cyan")
                    os.remove(os.path.join(path, file))
                    file_count += 1
                except Exception as e:
                    update_log(f"Error deleting {full_path}: {str(e)}\n", "red")
    
    if file_count > 0:
        update_log(f"\nGame «{game_name}» has been removed.\n\n", "green")
    else:
        update_log(f"\nThe AppID: {game_id} files were not found.\n\n", "yellow")


def view_all_games():
    games_text.configure(state="normal")
    games_text.delete('1.0', 'end')
    
    if not select_steam_path_flg:
        games_text.insert(customtkinter.END, "Select Steam folder for view game list")
        games_text.configure(state="disabled")
        return
        
    count = 0
    stplugin_path = steam_paths["stplugin"]
    
    for file in os.listdir(stplugin_path):
        if file.endswith("0.st"):
            game_id = file.replace(".st", "")
            count += 1
            game_name = get_game_name(game_id)
            games_text.insert(customtkinter.END, f"{count}. {game_name}  AppID: {game_id}\n")
            
    games_text.configure(state="disabled")


def delete_all_games():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    update_log("Deletion files...\n", "yellow")
    
    files_to_delete = []
    for path in steam_paths.values():
        if path is None:
            continue
            
        for file in os.listdir(path):
            if file.endswith((".st", ".manifest", ".bin")):
                files_to_delete.append(os.path.join(path, file))
    
    if askyesno(title="Delete all games?", message="Do you want to delete ALL games?"):
        for file in files_to_delete:
            try:
                os.remove(file)
                update_log(f"{file.replace('/', '\\')}\n", "cyan")
            except Exception as e:
                update_log(f"Error deleting {file}: {str(e)}\n", "red")
        update_log("The games have been successfully deleted!\n\n", "green")
    else:
        update_log("File deletion aborted...\n\n", "red")


def delete_steamtools():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    os.system("taskkill /f /im Steamtools.exe")
    
    stui_path = steam_paths["stui"]
    try:
        files_deleted = 0
        
        if os.path.exists(stui_path):
            for file in os.listdir(stui_path):
                full_path = os.path.join(stui_path, file)
                os.remove(full_path)
                update_log(f"Deleted: {full_path}\n", "cyan")
                files_deleted += 1
        
        if files_deleted > 0:
            update_log("The Steamtools have been successfully deleted!\n\n", "green")
        else:
            update_log("Steamtools has already been deleted.\n\n", "yellow")
    except Exception as e:
        update_log(f"Error: {str(e)}\n", "red")


def ask_delete_steamtools():
    update_log("Delete Steamtools?\n", "yellow")
    if askyesno(title="Delete Steamtools?", message="Do you want to delete Steamtools?"):
        delete_steamtools()
    else:
        update_log("Steamtools deletion aborted...\n\n", "red")


def browse_steam_folder():
    global steam_folder, select_steam_path_flg, steam_paths
    
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return
        
    if "config" not in os.listdir(folder_selected):
        show_message("Error", "Select valid steam folder!")
        return
        
    # Set steam folder and paths
    steam_folder = folder_selected
    steam_paths = {
        "stplugin": os.path.join(steam_folder, "config", "stplug-in"),
        "config_depotcache": os.path.join(steam_folder, "config", "depotcache"),
        "depotcache": os.path.join(steam_folder, "depotcache"),
        "stui": os.path.join(steam_folder, "config", "stUI"),
        "stats": os.path.join(steam_folder, "config", "StatsExport")
    }
    
    select_steam_path_flg = True
    
    entry_path.configure(state="normal")
    entry_path.delete(0, "end")
    entry_path.insert("1", steam_folder)
    entry_path.configure(state="disabled")
    
    # Load game list
    Thread(target=view_all_games).start()


def restart_steam():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    steam_exe = "Steam.exe"
    steam_path = os.path.join(steam_folder, steam_exe)
    
    update_log("Restarting Steam\n\n", "yellow")
    
    try:
        # Kill Steam if running
        subprocess.run(["taskkill", "/f", "/im", steam_exe], check=True)
    except:
        pass
    
    try:
        if os.path.exists(steam_path):
            subprocess.Popen(steam_path, shell=True)
            update_log("Steam has been restarted.\n\n", "green")
        else:
            update_log("Steam.exe not found in the selected folder.\n", "red")
    except Exception as e:
        update_log(f"Error: {str(e)}\n", "red")


def setup_ui():
    global root, entry_path, files_text, games_text, entry_id
    
    root = customtkinter.CTk()
    root.title("Steamtools remover")
    root.geometry("1200x600")
    root.resizable(False, False)
    
    c = Canvas(root, width=2000, height=1000, bg="#242424", borderwidth=0, highlightthickness=0)
    c.place(x=0, y=0)
    
    c.create_text(120, 33, text="Select Steam folder", fill="white", font=("Helvetica", 13))
    c.create_line(20, 35, 40, 35, width=1, fill="#565B5E")
    c.create_line(200, 35, 724, 35, width=1, fill="#565B5E")
    c.create_line(20, 35, 20, 97, width=1, fill="#565B5E")
    c.create_line(724, 35, 724, 97, width=1, fill="#565B5E")
    c.create_line(20, 97, 724, 97, width=1, fill="#565B5E")
    
    entry_path = customtkinter.CTkEntry(master=root, placeholder_text="Enter the path "+"-"*120+">", width=480, height=30)
    entry_path.place(y=55, x=30)
    entry_path.configure(state="disabled")
    
    browse_button = customtkinter.CTkButton(master=root, text="...", corner_radius=8, width=40, command=browse_steam_folder)
    browse_button.place(y=55, x=520)
    
    c.create_text(75, 110, text="Options", fill="white", font=("Helvetica", 13))
    c.create_line(20, 110, 40, 110, width=1, fill="#565B5E")
    c.create_line(110, 110, 724, 110, width=1, fill="#565B5E")
    c.create_line(20, 110, 20, 222, width=1, fill="#565B5E")
    c.create_line(724, 110, 724, 222, width=1, fill="#565B5E")
    c.create_line(20, 222, 724, 222, width=1, fill="#565B5E")
    c.create_line(260, 110, 260, 222, width=1, fill="#565B5E")
    c.create_line(527, 110, 527, 222, width=1, fill="#565B5E")
    
    # Option buttons - first row
    delete_button = customtkinter.CTkButton(
        master=root, 
        text="Delete a SteamTools game",
        corner_radius=8, 
        command=lambda: setup_delete_game(), 
        width=140
    )
    delete_button.place(x=40, y=140)
    
    delete_all_button = customtkinter.CTkButton(
        master=root, 
        text="Delete ALL SteamTools game",
        corner_radius=8, 
        command=delete_all_games, 
        width=180
    )
    delete_all_button.place(x=280, y=140)
    
    channel_button = customtkinter.CTkButton(
        master=root, 
        text="Channel with games",
        corner_radius=8, 
        command=lambda: webbrowser.open('https://piped.wireway.ch/watch?v=dQw4w9WgXcQ'), 
        width=140
    )
    channel_button.place(x=550, y=140)
    
    delete_steamtools_button = customtkinter.CTkButton(
        master=root, 
        text="Delete SteamTools",
        corner_radius=8, 
        command=ask_delete_steamtools, 
        width=180
    )
    delete_steamtools_button.place(x=280, y=180)
    
    # Games list section
    c.create_text(113, 240, text="SteamTools games", fill="white", font=("Helvetica", 13))
    c.create_line(20, 240, 40, 240, width=1, fill="#565B5E")
    c.create_line(188, 240, 724, 240, width=1, fill="#565B5E")
    c.create_line(20, 240, 20, 580, width=1, fill="#565B5E")
    c.create_line(724, 240, 724, 580, width=1, fill="#565B5E")
    c.create_line(20, 580, 724, 580, width=1, fill="#565B5E")
    
    games_text = customtkinter.CTkTextbox(master=root, width=684, height=310)
    games_text.place(y=260, x=30)
    
    refresh_button = customtkinter.CTkButton(
        master=root, 
        text="Refresh", 
        corner_radius=8, 
        width=100, 
        command=lambda: Thread(target=view_all_games).start()
    )
    refresh_button.place(x=30, y=540)
    
    c.create_text(810, 33, text="Progress", fill="white", font=("Helvetica", 13))
    c.create_line(744, 35, 744, 580, width=1, fill="#565B5E")
    c.create_line(744, 35, 770, 35, width=1, fill="#565B5E")
    c.create_line(850, 35, 1180, 35, width=1, fill="#565B5E")
    c.create_line(1180, 35, 1180, 580, width=1, fill="#565B5E")
    c.create_line(744, 580, 1180, 580, width=1, fill="#565B5E")
    
    files_text = customtkinter.CTkTextbox(master=root, width=416, height=505)
    files_text.place(y=55, x=754)
    files_text.configure(state="disabled")
    
    exit_button = customtkinter.CTkButton(
        master=root, 
        text="Exit", 
        corner_radius=8, 
        width=100, 
        command=lambda: root.destroy()
    )
    exit_button.place(x=1070, y=540)
    
    restart_button = customtkinter.CTkButton(
        master=root, 
        text="Restart Steam", 
        corner_radius=8,
        width=100, 
        command=restart_steam
    )
    restart_button.place(x=960, y=540)
    
    Thread(target=view_all_games).start()


def setup_delete_game():
    global entry_id
    
    entry_id = customtkinter.CTkEntry(master=root, placeholder_text="Enter ID", width=107, height=30)
    entry_id.place(x=40, y=180)
    
    get_id_button = customtkinter.CTkButton(master=root, corner_radius=8, text="Delete", width=60, command=delete_game)
    get_id_button.place(x=150, y=180)


if __name__ == "__main__":
    setup_ui()
    root.mainloop()