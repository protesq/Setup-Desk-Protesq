
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import os
from threading import Thread
import webbrowser

# İndirme bağlantıları
download_links = {
    "Web Browsers": {
        "Chrome": "https://dl.google.com/chrome/install/latest/chrome_installer.exe",
        "Opera": "https://get.geo.opera.com/pub/opera/desktop/95.0.4635.37/win/Opera_95.0.4635.37_Setup.exe",
        "Firefox": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US",
        "Brave": "https://laptop-updates.brave.com/latest/winx64"
    },
    "Developer Tools": {
        "Python x64 3": "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe",
        "Python 3": "https://www.python.org/ftp/python/3.10.9/python-3.10.9.exe",
        "FileZilla": "https://download.filezilla-project.org/client/FileZilla_3.68.1_win64_sponsored2-setup.exe",
        "Notepad++": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.7.1/npp.8.7.1.Installer.x64.exe",
        "Visual Studio": "https://aka.ms/vs/17/release/vs_community.exe",
        "Visual Studio Code": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
        "GitHub Desktop": "https://desktop.github.com/download/",  # linke gider
        "Android Studio": "https://r3---sn-n4v7sn7s.gvt1.com/edgedl/android/studio/install/2022.1.1.21/android-studio-2022.1.1.21-windows.exe",
        "Unity Hub": "https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.exe",
        "VirtualBox": "https://download.virtualbox.org/virtualbox/7.0.10/VirtualBox-7.0.10-158379-Win.exe"
    },
    "Office Alternatives": {
        "LibreOffice": "https://www.libreoffice.org/download/download-libreoffice/",
        "OnlyOffice": "https://www.onlyoffice.com/en/download-desktop.aspx",
        "WPS Office": "https://www.wps.com/download/",
        "OpenOffice": "https://www.openoffice.org/download/index.html"
    },
    "Games": {
        "Steam": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe",
        "Epic Games": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"
    },
    "Media": {
        "VLC": "https://get.videolan.org/vlc/3.0.21/win32/vlc-3.0.21-win32.exe",  # linke gider
        "Spotify": "https://download.scdn.co/SpotifySetup.exe",
        "Audacity": "https://github.com/audacity/audacity/releases/download/Audacity-3.2.5/audacity-win-3.2.5-x64.exe",
        "CapCut": "https://lf16-capcut.faceulv.com/obj/capcutpc-packages-us/installer/capcut_capcutpc_0_1.2.6_installer.exe",  # linke gider
        "OBS Studio": "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-29.0.2-Full-Installer-x64.exe"
    }
}

open_in_browser = {"CapCut", "VLC", "GitHub Desktop", "LibreOffice", "OnlyOffice", "WPS Office", "OpenOffice"}

download_directory = ""

def prompt_download_directory():
    global download_directory
    if not download_directory:
        download_directory = filedialog.askdirectory(title="İndirme Klasörünü Seçin")
        if not download_directory:
            messagebox.showerror("Hata", "İndirme klasörü seçilmedi. Program kapatılıyor.")
            exit()

def change_download_directory(output_widget):
    global download_directory
    new_directory = filedialog.askdirectory(title="Yeni İndirme Klasörünü Seçin")
    if new_directory:
        download_directory = new_directory
        output_widget.insert(tk.END, f"İndirme klasörü değiştirildi: {download_directory}\n")
    else:
        output_widget.insert(tk.END, "İndirme klasörü değiştirilmedi.\n")

# İndirme fonksiyonu
def download_file(name, url, output_widget, progress_bar, retries=3):
    if name in open_in_browser:
        output_widget.insert(tk.END, f"{name} tarayıcıda açılıyor...\n")
        output_widget.update()
        webbrowser.open(url)
        return

    try:
        output_widget.insert(tk.END, f"{name} indiriliyor...\n")
        output_widget.update()

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        os.makedirs(download_directory, exist_ok=True)

        # Dosya adı temizleme
        filename = url.split("/")[-1].split("?")[0]
        if not filename:
            filename = f"{name.replace(' ', '_')}.exe"
        filepath = os.path.join(download_directory, filename)

        for attempt in range(retries):
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress = (downloaded_size / total_size) * 100 if total_size else 0
                        progress_bar["value"] = progress
                        progress_bar.update()

            if os.path.exists(filepath) and os.path.getsize(filepath) == total_size:
                output_widget.insert(tk.END, f"{name} başarıyla indirildi.\nDosya konumu: {filepath}\n\n")
                return
            else:
                output_widget.insert(tk.END, f"{name} indirilemedi, tekrar deneniyor ({attempt + 1}/{retries})...\n")

        output_widget.insert(tk.END, f"{name} indirme denemeleri başarısız oldu.\n")
        if os.path.exists(filepath):
            os.remove(filepath)

    except requests.exceptions.RequestException as e:
        output_widget.insert(tk.END, f"{name} indirilirken hata oluştu: {e}\n")
    except Exception as e:
        output_widget.insert(tk.END, f"{name} indirilirken beklenmeyen bir hata oluştu: {e}\n")
    finally:
        output_widget.update()
        progress_bar["value"] = 0

# Seçilen dosyaları indirme
def download_selected(output_widget, check_vars, progress_bar):
    output_widget.delete(1.0, tk.END)
    selected_items = [name for category, items in check_vars.items() for name, var in items.items() if var.get()]
    if not selected_items:
        messagebox.showwarning("Uyarı", "Lütfen en az bir program seçin!")
        return

    def download_all():
        for category, items in check_vars.items():
            for name, var in items.items():
                if var.get():
                    url = download_links[category].get(name)
                    if url:
                        download_file(name, url, output_widget, progress_bar)
        output_widget.insert(tk.END, "Tüm indirmeler tamamlandı.\n")

    Thread(target=download_all).start()

# GUI oluşturma
def create_gui():
    global download_directory
    prompt_download_directory()

    root = tk.Tk()
    root.title("Program İndirme Aracı")
    root.geometry("1400x700")
    root.resizable(False, False)

    title = tk.Label(root, text="Program İndirme Aracı", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    check_vars = {}

    for col, (category, items) in enumerate(download_links.items()):
        category_frame = tk.Frame(main_frame)
        category_frame.grid(row=0, column=col, padx=20, pady=10, sticky="n")

        category_label = tk.Label(category_frame, text=category, font=("Arial", 12, "bold"))
        category_label.pack(anchor="w")

        check_vars[category] = {}
        for name in items.keys():
            var = tk.BooleanVar()
            check = tk.Checkbutton(category_frame, text=name, variable=var)
            check.pack(anchor="w", padx=10, pady=2)
            check_vars[category][name] = var

    output_label = tk.Label(root, text="İndirme Durumu:", font=("Arial", 12))
    output_label.pack(pady=5)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=5)

    output_text = tk.Text(root, height=10)
    output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    download_button = tk.Button(button_frame, text="İndir", bg="green", fg="white", width=15,
                                 command=lambda: download_selected(output_text, check_vars, progress_bar))
    download_button.pack(side=tk.LEFT, padx=10)

    directory_button = tk.Button(button_frame, text="İndirme Klasörü", bg="blue", fg="white", width=15,
                                  command=lambda: change_download_directory(output_text))
    directory_button.pack(side=tk.LEFT, padx=10)

    exit_button = tk.Button(button_frame, text="Çıkış", bg="red", fg="white", width=15, command=root.quit)
    exit_button.pack(side=tk.RIGHT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
