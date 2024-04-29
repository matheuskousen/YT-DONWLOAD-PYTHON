import tkinter as tk
from tkinter import filedialog, messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip
import threading
import os

class DownloadManager:
    def __init__(self):
        self.download_threads = []

    def add_download(self, url, destination, convert_to_audio):
        thread = threading.Thread(target=self.download_audio, args=(url, destination, convert_to_audio))
        self.download_threads.append(thread)
        thread.start()

    def download_audio(self, url, destination, convert_to_audio):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            audio_path = stream.download(output_path=destination)
            if convert_to_audio:
                audio_path = self.convert_to_mp3(audio_path)
            else:
                # Renomeia o arquivo de áudio com extensão .mp3
                mp3_path = os.path.splitext(audio_path)[0] + ".mp3"
                os.rename(audio_path, mp3_path)
            messagebox.showinfo("Concluído", "Download e conversão concluídos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao baixar o áudio: {str(e)}")

    def convert_to_mp3(self, audio_path):
        # Gera o caminho para o arquivo de áudio convertido para MP3
        mp3_path = os.path.splitext(audio_path)[0] + ".mp3"
        # Carrega o arquivo de áudio
        audio_clip = AudioFileClip(audio_path)
        # Salva o arquivo de áudio como MP3
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()
        # Remove o arquivo de áudio original
        os.remove(audio_path)
        return mp3_path

def choose_directory():
    directory = filedialog.askdirectory()
    destination_path.set(directory)

def download_all():
    urls = [url_entry.get() for url_entry in url_entries]
    destination = destination_path.get()
    convert_to_audio = audio_option_var.get()
    if not destination:
        messagebox.showerror("Erro", "Selecione uma pasta de destino!")
        return
    for url in urls:
        if url.strip():
            download_manager.add_download(url.strip(), destination, convert_to_audio)
    status_label.config(text="Downloads iniciados!")

# Criando a interface
root = tk.Tk()
root.title("YouTube Downloader")

# Criando os widgets
url_entries = []

for i in range(10):
    url_label = tk.Label(root, text=f"URL do vídeo {i + 1}:")
    url_label.grid(row=i, column=0, sticky="w", padx=(10, 5), pady=5)

    url_entry = tk.Entry(root, width=50)
    url_entry.grid(row=i, column=1, padx=(0, 10), pady=5)
    url_entries.append(url_entry)

destination_frame = tk.Frame(root)
destination_frame.grid(row=10, column=0, columnspan=2, pady=(10,0), padx=10, sticky="ew")

destination_label = tk.Label(destination_frame, text="Pasta de destino:")
destination_label.pack(side="left")

destination_path = tk.StringVar()
destination_entry = tk.Entry(destination_frame, textvariable=destination_path, width=40)
destination_entry.pack(side="left", padx=(5,0))

choose_directory_button = tk.Button(destination_frame, text="Escolher Pasta", command=choose_directory)
choose_directory_button.pack(side="left", padx=(5,0))

audio_option_var = tk.BooleanVar()
audio_option_checkbox = tk.Checkbutton(root, text="Baixar e Converter para MP3", variable=audio_option_var)
audio_option_checkbox.grid(row=11, column=0, columnspan=2, pady=5)

download_all_button = tk.Button(root, text="Baixar Todos", command=download_all, width=20)
download_all_button.grid(row=12, column=0, columnspan=2, pady=(0, 10))

status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=13, column=0, columnspan=2, pady=(0, 10))

download_manager = DownloadManager()

# Iniciando o loop da interface
root.mainloop()