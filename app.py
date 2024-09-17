import yt_dlp as youtube_dl
from moviepy.editor import *
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
import re
import threading
import winsound
from urllib.parse import urlparse
import clipboard  # Para acessar a área de transferência
import json

# Função para limpar nomes de arquivos
def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Função para validar URLs
def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

# Função para verificar disponibilidade do vídeo
def check_video_availability(url):
    try:
        with youtube_dl.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except Exception:
        return False

# Função para carregar configurações do usuário
def load_user_settings():
    try:
        with open("user_settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"last_save_directory": "", "quality": "high"}

# Função para salvar configurações do usuário
def save_user_settings(settings):
    with open("user_settings.json", "w") as file:
        json.dump(settings, file)

# Função para baixar e converter vídeos
def download_video(url, save_directory, quality, progress_var, index, status_labels, retry=0):
    try:
        ydl_opts = {
            'format': f'bestaudio[ext=webm]/bestaudio/best' if quality == "high" else ('worstaudio[ext=webm]/worstaudio' if quality == "low" else 'bestaudio[ext=webm]/bestaudio'),
            'outtmpl': os.path.join(save_directory, 'temp_audio.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)

        safe_title = clean_filename(video_title)
        mp3_path = os.path.join(save_directory, f"{safe_title}.mp3")

        audio_clip = AudioFileClip(os.path.join(save_directory, "temp_audio.webm"))
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()

        os.remove(os.path.join(save_directory, "temp_audio.webm"))

        progress_var.set(progress_var.get() + 1)
        status_labels[index].config(text="✔️ Sucesso", foreground="green")
        return f"Download e conversão concluídos para: {mp3_path}"
    except Exception as e:
        if retry < 3:
            return download_video(url, save_directory, quality, progress_var, index, status_labels, retry=retry+1)
        progress_var.set(progress_var.get() + 1)
        status_labels[index].config(text="❌ Erro", foreground="red")
        log_error(f"Erro ao processar {url}: {e}")
        return f"Erro ao processar {url}: {e}"

# Função para executar downloads em threads
def download_videos():
    save_directory = filedialog.askdirectory(initialdir=user_settings["last_save_directory"], title="Selecione o diretório para salvar os arquivos MP3")
    if not save_directory:
        messagebox.showerror("Erro", "Por favor, selecione um diretório para salvar os arquivos.")
        return

    # Atualiza as configurações do usuário com o diretório de download atual
    user_settings["last_save_directory"] = save_directory
    save_user_settings(user_settings)

    urls = [entry.get().strip() for entry in url_entries if entry.get().strip()]
    if not urls:
        messagebox.showwarning("Aviso", "Nenhum URL foi inserido.")
        return

    invalid_urls = [url for url in urls if not is_valid_url(url) or not check_video_availability(url)]
    if invalid_urls:
        messagebox.showerror("Erro", f"URLs inválidas ou indisponíveis:\n{', '.join(invalid_urls)}")
        return

    progress_var.set(0)
    progress_bar["maximum"] = len(urls)
    
    results = []
    
    def run_downloads():
        for index, url in enumerate(urls):
            result = download_video(url, save_directory, user_settings["quality"], progress_var, index, status_labels)
            results.append(result)
        
        winsound.Beep(1000, 500)  # Sinaliza finalização
        messagebox.showinfo("Resultados", "\n".join(results))
    
    threading.Thread(target=run_downloads).start()

# Função para limpar campos
def clear_fields():
    for entry in url_entries:
        entry.delete(0, tk.END)
    for label in status_labels:
        label.config(text="")

# Função para colar múltiplas URLs
def paste_urls():
    clipboard_content = clipboard.paste().split()
    for i, url in enumerate(clipboard_content[:5]):
        url_entries[i].insert(0, url)

# Função para log de erros
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

# Função para ajustar a qualidade do áudio
def set_quality(value):
    user_settings["quality"] = value
    save_user_settings(user_settings)

# Carregar configurações do usuário
user_settings = load_user_settings()

# Interface Gráfica com Tkinter
root = tk.Tk()
root.title("YouTube para MP3")
root.geometry("900x750")

# Aplicar tema moderno
style = ttk.Style()
style.theme_use('clam')

# Frame principal com barra de rolagem
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Lista para armazenar os campos de entrada de URL e status
url_entries = []
status_labels = []

# Adiciona 5 campos de entrada no frame rolável
for i in range(5):
    row_frame = tk.Frame(scrollable_frame)
    row_frame.pack(pady=5, anchor='w')
    
    tk.Label(row_frame, text=f"URL do vídeo {i+1}:").pack(side=tk.LEFT, padx=5)
    entry = tk.Entry(row_frame, width=60)
    entry.pack(side=tk.LEFT, padx=5)
    url_entries.append(entry)
    
    status_label = tk.Label(row_frame, text="", width=10)
    status_label.pack(side=tk.LEFT, padx=5)
    status_labels.append(status_label)

# Barra de progresso
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=5)
progress_bar.pack(pady=20, padx=10, fill=tk.X)

# Frame para configurações
settings_frame = tk.LabelFrame(root, text="Configurações", padx=10, pady=10)
settings_frame.pack(padx=10, pady=10)

quality_label = tk.Label(settings_frame, text="Qualidade de Áudio:")
quality_label.pack(side=tk.LEFT)

quality_options = ["high", "medium", "low"]
quality_combobox = ttk.Combobox(settings_frame, values=quality_options)
quality_combobox.set(user_settings["quality"])
quality_combobox.pack(side=tk.LEFT, padx=10)
quality_combobox.bind("<<ComboboxSelected>>", lambda event: set_quality(quality_combobox.get()))

# Botões de controle
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

download_button = tk.Button(button_frame, text="Baixar e Converter", command=download_videos)
download_button.grid(row=0, column=0, padx=5)

paste_button = tk.Button(button_frame, text="Colar URLs", command=paste_urls)
paste_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(button_frame, text="Limpar Campos", command=clear_fields)
clear_button.grid(row=0, column=2, padx=5)

exit_button = tk.Button(button_frame, text="Sair", command=root.quit)
exit_button.grid(row=0, column=3, padx=5)

# Inicia o loop da interface
root.mainloop()
