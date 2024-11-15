import os
import shutil
import logging
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

# Define VirusTotal API key here
VIRUSTOTAL_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# File categories for sorting
FILE_CATEGORIES = {
    "Images & Graphics": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".ico", ".webp"],
    "Documents & Text Files": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".xlsx", ".xls", ".csv", ".pptx", ".ppt", ".md"],
    "Audio & Music": [".mp3", ".aac", ".wav", ".flac", ".ogg", ".m4a", ".wma", ".aiff"],
    "Videos & Movies": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm", ".mpeg"],
    "Code & Scripts": [".py", ".js", ".sh", ".html", ".css", ".java", ".cpp", ".c", ".cs", ".ipynb", ".php", ".go", ".rb", ".swift", ".rs", ".ts", ".kt"],
    "Compressed Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Applications & Executables": [".exe", ".apk", ".dmg", ".app", ".deb", ".bin", ".msi", ".bat"],
    "eBooks & Reading": [".epub", ".mobi", ".azw3", ".fb2", ".ibooks", ".djvu"],
    "CAD & Design Files": [".dwg", ".dxf", ".skp", ".3ds", ".obj", ".blend", ".stl"],
    "Fonts & Typography": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "Spreadsheets & Data": [".xls", ".xlsx", ".csv", ".ods"],
    "Presentations": [".ppt", ".pptx", ".key"],
    "Database Files": [".sql", ".db", ".sqlite", ".mdb", ".accdb"],
    "Project Files": [".psd", ".ai", ".indd", ".xd", ".fla", ".sketch", ".fig"],
    "Torrents & Downloads": [".torrent", ".crdownload", ".part", ".tmp"],
    "Web Files": [".html", ".htm", ".css", ".js", ".php", ".xml", ".json"],
    "Miscellaneous": [".log", ".bak", ".old", ".cfg", ".ini"]
}

logging.basicConfig(filename="file_organizer.log", level=logging.INFO, format="%(asctime)s - %(message)s", filemode='w')

def scan_file_virustotal(file_path):
    """
    Function to scan a file with VirusTotal API.
    """
    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, headers=headers, files=files)
        
    if response.status_code == 200:
        scan_id = response.json()["data"]["id"]
        return scan_id
    else:
        logging.error(f"Error scanning file '{file_path}' with VirusTotal.")
        return None

def get_scan_report(scan_id):
    """
    Function to get the scan report from VirusTotal.
    """
    url = f"https://www.virustotal.com/api/v3/analyses/{scan_id}"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        report = response.json()
        malicious = report["data"]["attributes"]["stats"]["malicious"]
        return malicious > 0  # True if malicious, False otherwise
    else:
        logging.error("Error retrieving scan report.")
        return False

def organize_folder(folder_path):
    folder_path = os.path.normpath(folder_path)
    if not os.path.isdir(folder_path):
        logging.error(f"The folder '{folder_path}' does not exist.")
        messagebox.showerror("Error", f"The folder '{folder_path}' does not exist.")
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Check if the file is malicious
        scan_id = scan_file_virustotal(file_path)
        if scan_id:
            is_malicious = get_scan_report(scan_id)
            if is_malicious:
                quarantine_folder = os.path.join(folder_path, "Quarantine")
                os.makedirs(quarantine_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(quarantine_folder, filename))
                logging.warning(f"Moved '{filename}' to 'Quarantine' due to malware detection.")
                continue  # Skip the rest of the categorization for this file

        # Continue with organizing
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower().strip()

        moved = False
        for category, extensions in FILE_CATEGORIES.items():
            if file_extension in extensions:
                category_folder = os.path.join(folder_path, category)
                os.makedirs(category_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(category_folder, filename))
                logging.info(f"Moved '{filename}' to '{category}' folder.")
                moved = True
                break

        if not moved:
            others_folder = os.path.join(folder_path, "Others")
            os.makedirs(others_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(others_folder, filename))
            logging.info(f"Moved '{filename}' to 'Others' folder.")

    messagebox.showinfo("Sorting Complete", "Finished sorting your files")

# GUI Code
def browse_folder():
     folder_path = filedialog.askdirectory()
     if folder_path:
          organize_folder(folder_path)

root = tk.Tk()
root.title("File Organizer")
root.geometry("450x250")

label = tk.Label(root, text="Choose a folder to organize its files", font=("Open Sans", 16))
label.pack(pady=20)

browse_button = tk.Button(root, text="Browse Folder", command=browse_folder)
browse_button.pack(pady=20)

root.mainloop()
