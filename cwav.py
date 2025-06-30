import os
import sys
import zipfile
import pygame
import io
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

def create_cwav(wav_path):
    base = os.path.splitext(os.path.basename(wav_path))[0]
    output_path = filedialog.asksaveasfilename(defaultextension=".cwav", initialfile=f"{base}.cwav", filetypes=[("Compressed WAV", "*.cwav")])
    if not output_path:
        return
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(wav_path, arcname=os.path.basename(wav_path))
        messagebox.showinfo("Success", f"Created: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create .cwav:\n{e}")

def play_cwav(cwav_path):
    try:
        with zipfile.ZipFile(cwav_path, 'r') as zip_ref:
            wav_files = [f for f in zip_ref.namelist() if f.lower().endswith('.wav')]
            if not wav_files:
                messagebox.showerror("Error", "No .wav file found in the archive.")
                return
            wav_data = zip_ref.read(wav_files[0])
            wav_buffer = io.BytesIO(wav_data)
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "Invalid .cwav file.")
        return
    pygame.mixer.init()
    pygame.mixer.music.load(wav_buffer)
    pygame.mixer.music.play()
    def check_done():
        if pygame.mixer.music.get_busy():
            root.after(100, check_done)
        else:
            messagebox.showinfo("Done", "Playback finished.")
    check_done()

def handle_drop(event):
    path = event.data.strip('{}')
    if path.lower().endswith('.wav'):
        create_cwav(path)
    elif path.lower().endswith('.cwav'):
        play_cwav(path)
    else:
        messagebox.showerror("Unsupported File", "Only .wav and .cwav files are supported.")

def select_wav():
    wav_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if wav_path:
        create_cwav(wav_path)

def select_cwav():
    cwav_path = filedialog.askopenfilename(filetypes=[("Compressed WAV", "*.cwav")])
    if cwav_path:
        play_cwav(cwav_path)

def quit_app():
    root.quit()

root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
root.title("CWAV Tool")
root.geometry("420x250")
root.resizable(False, False)

tk.Label(root, text="Compressed Waveform (.cwav) Tool", font=("Segoe UI", 14)).pack(pady=10)
tk.Button(root, text="Create .cwav from .wav", width=30, command=select_wav).pack(pady=5)
tk.Button(root, text="Play .cwav file", width=30, command=select_cwav).pack(pady=5)
tk.Button(root, text="Quit", width=30, command=quit_app).pack(pady=5)

if DND_AVAILABLE:
    drop_area = tk.Label(root, text="Drag & drop .wav or .cwav file here", fg="gray", relief="groove", width=45, height=3)
    drop_area.pack(pady=15)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind('<<Drop>>', handle_drop)

root.mainloop()