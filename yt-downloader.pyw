import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class YTDownloader:

    def __init__(self, root):
        self.root = root
        self.root.title("yt-downloader (Windows Version)")
        self.root.geometry("1024x720")

        # Mendapatkan path absolut dari folder tempat script ini berjalan
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Menentukan path file .exe di folder lokal yang sama
        self.ytdlp_path = os.path.join(self.current_dir, "yt-dlp.exe")
        self.mpv_path = os.path.join(self.current_dir, "mpv.exe")

        # Variabel Utama
        self.url_var = tk.StringVar()
        self.video_format_var = tk.StringVar(value="299")  
        self.audio_format_var = tk.StringVar(value="140")  
        self.ext_video_var = tk.StringVar(value="mp4")
        self.audio_only_ext_var = tk.StringVar(value="mp3")
        self.stream_res_var = tk.StringVar(value="1080p")

        self.create_widgets()
        self.check_dependencies_exist()

    def check_dependencies_exist(self):
        """Memeriksa apakah berkas exe yang dibutuhkan ada di folder lokal."""
        missing = []
        if not os.path.exists(self.ytdlp_path):
            missing.append("yt-dlp.exe")
        if not os.path.exists(self.mpv_path):
            missing.append("mpv.exe")
            
        if missing:
            messagebox.showwarning(
                "Peringatan Dependensi", 
                f"Berkas berikut tidak ditemukan di folder script:\n{', '.join(missing)}\n\n"
                f"Pastikan diletakkan di:\n{self.current_dir}"
            )

    def create_widgets(self):
        # --- Section 1: URL Input ---
        url_frame = tk.LabelFrame(self.root, text=" 1. Input URL YouTube ", padx=10, pady=10)
        url_frame.pack(fill="x", padx=10, pady=5)

        # Membuat Entry URL
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=("Arial", 11))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Menu Klik Kanan Paste (opsional tetap dipertahankan)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_url)
        self.url_entry.bind("<Button-3>", self.show_context_menu)

        # Tombol Get Formats (Paling Kanan)
        self.btn_get = tk.Button(
            url_frame, text="Get Formats", command=self.start_get_formats, bg="#2196F3", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_get.pack(side="right", padx=5)

        # Tombol Reset URL (Tengah)
        self.btn_reset = tk.Button(
            url_frame, text="Reset", command=self.reset_url_and_logs, bg="#F44336", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_reset.pack(side="right", padx=5)

        # Tombol Paste URL (Kiri/Sebelum Reset - FITUR BARU)
        self.btn_paste = tk.Button(
            url_frame, text="Paste", command=self.paste_url, bg="#00BCD4", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_paste.pack(side="right", padx=5)

        # --- Section 2: Terminal Output Textbox ---
        output_frame = tk.LabelFrame(self.root, text=" Available Formats (yt-dlp -F) ", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_output = tk.Text(output_frame, font=("Courier", 9), wrap="none")
        scrollbar_y = tk.Scrollbar(self.txt_output, orient="vertical", command=self.txt_output.yview)
        scrollbar_x = tk.Scrollbar(self.txt_output, orient="horizontal", command=self.txt_output.xview)
        self.txt_output.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.txt_output.pack(fill="both", expand=True)

        # --- Section 3: Tabs (Video, Audio & Streaming Options) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="x", padx=10, pady=5)

        # Tab Video
        self.tab_video = tk.Frame(self.notebook)
        self.notebook.add(self.tab_video, text="  Video Options  ")
        
        tk.Label(self.tab_video, text="Video ID:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.tab_video, textvariable=self.video_format_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(self.tab_video, text="Audio ID:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.tab_video, textvariable=self.audio_format_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(self.tab_video, text="Container:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        cb_video_ext = ttk.Combobox(self.tab_video, textvariable=self.ext_video_var, values=["mp4", "mkv"], width=8, state="readonly")
        cb_video_ext.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Tab Audio
        self.tab_audio = tk.Frame(self.notebook)
        self.notebook.add(self.tab_audio, text="  Audio Only  ")
        
        tk.Label(self.tab_audio, text="Format Audio:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        cb_audio_ext = ttk.Combobox(self.tab_audio, textvariable=self.audio_only_ext_var, values=["mp3", "m4a"], width=8, state="readonly")
        cb_audio_ext.grid(row=0, column=1, sticky="w", padx=5, pady=10)

        # Tab Streaming
        self.tab_stream = tk.Frame(self.notebook)
        self.notebook.add(self.tab_stream, text="  Streaming (mpv)  ")
        
        tk.Label(self.tab_stream, text="Maksimal Resolusi:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        cb_stream_res = ttk.Combobox(
            self.tab_stream, 
            textvariable=self.stream_res_var, 
            values=["2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"], 
            width=12, 
            state="readonly"
        )
        cb_stream_res.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        
        self.btn_stream = tk.Button(
            self.tab_stream, text="PLAY IN MPV", command=self.start_streaming, bg="#9C27B0", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_stream.grid(row=0, column=2, padx=20, pady=10)

        # --- Section 4: Download Button ---
        self.btn_download = tk.Button(
            self.root, text="DOWNLOAD", command=self.start_download, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2
        )
        self.btn_download.pack(fill="x", padx=10, pady=10)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        active_tab = self.notebook.index(self.notebook.select())
        if active_tab == 2:
            self.btn_download.config(state="disabled")
        else:
            self.btn_download.config(state="normal")

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def paste_url(self):
        """Mengambil teks dari clipboard sistem dan memasukkannya ke Entry URL."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_var.set(clipboard_text.strip())
        except tk.TclError:
            pass

    def reset_url_and_logs(self):
        """Mengosongkan kolom input URL dan membersihkan isi textbox log."""
        self.url_var.set("")
        self.txt_output.delete("1.0", tk.END)

    def log_message(self, message):
        self.txt_output.insert(tk.END, message)
        self.txt_output.see(tk.END)

    def start_get_formats(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Masukkan URL YouTube terlebih dahulu!")
            return

        if not os.path.exists(self.ytdlp_path):
            messagebox.showerror("Error", "yt-dlp.exe tidak ditemukan di folder lokal script!")
            return

        self.btn_get.config(state="disabled")
        self.txt_output.delete("1.0", tk.END)
        self.log_message("Mengambil informasi format dari yt-dlp... Mohon tunggu...\n\n")
        
        threading.Thread(target=self.run_get_formats, args=(url,), daemon=True).start()

    def run_get_formats(self, url):
        try:
            process = subprocess.Popen(
                [self.ytdlp_path, "-F", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                self.root.after(0, self.log_message, line)
            process.wait()
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Terjadi kesalahan: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_get.config(state="normal"))

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Masukkan URL YouTube terlebih dahulu!")
            return

        if not os.path.exists(self.ytdlp_path):
            messagebox.showerror("Error", "yt-dlp.exe tidak ditemukan di folder lokal script!")
            return

        download_dir = filedialog.askdirectory(title="Pilih Tempat Penyimpanan")
        if not download_dir:
            return  

        self.btn_download.config(state="disabled")
        self.txt_output.delete("1.0", tk.END)
        
        threading.Thread(target=self.run_download, args=(url, download_dir), daemon=True).start()

    def run_download(self, url, download_dir):
        output_template = os.path.join(download_dir, "%(title)s.%(ext)s")
        active_tab = self.notebook.index(self.notebook.select())
        
        cmd = [self.ytdlp_path, "-o", output_template]
        
        if active_tab == 0:
            vid = self.video_format_var.get().strip()
            aid = self.audio_format_var.get().strip()
            container = self.ext_video_var.get()
            cmd.extend(["-f", f"{vid}+{aid}", "--merge-output-format", container, url])
            self.root.after(0, self.log_message, f"Memulai download Video ({vid}+{aid}) ke dalam format {container}...\n\n")
        elif active_tab == 1:
            audio_ext = self.audio_only_ext_var.get()
            cmd.extend(["-x", "--audio-format", audio_ext, url])
            self.root.after(0, self.log_message, f"Memulai download Audio saja ({audio_ext})...\n\n")

        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                self.root.after(0, self.log_message, line)
            process.wait()
            
            if process.returncode == 0:
                self.root.after(0, messagebox.showinfo, "Sukses", "Download Berhasil Selesai!")
            else:
                self.root.after(0, messagebox.showerror, "Error", "Terjadi kesalahan saat mendownload.")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Gagal menjalankan perintah: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_download.config(state="normal"))

    def start_streaming(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Masukkan URL YouTube terlebih dahulu!")
            return

        if not os.path.exists(self.mpv_path):
            messagebox.showerror("Error", "mpv.exe tidak ditemukan di folder lokal script!")
            return

        self.btn_stream.config(state="disabled")
        self.txt_output.delete("1.0", tk.END)
        self.log_message(f"Membuka MPV untuk streaming dengan resolusi target {self.stream_res_var.get()}...\n")

        threading.Thread(target=self.run_mpv_stream, args=(url,), daemon=True).start()

    def run_mpv_stream(self, url):
        res_raw = self.stream_res_var.get()
        res_height = res_raw.split()[0].replace('p', '')

        ytdl_format_arg = f"bestvideo[height<={res_height}][vcodec!=av01]+bestaudio/best"

        cmd = [
            self.mpv_path,
            f"--ytdl-format={ytdl_format_arg}",
            url
        ]

        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                self.root.after(0, self.log_message, line)
            process.wait()
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Gagal memutar streaming: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_stream.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = YTDownloader(root)
    root.mainloop()
