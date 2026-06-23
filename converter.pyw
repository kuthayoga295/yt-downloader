import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# Memastikan ffmpeg.exe ada di folder yang sama dengan script
FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

class FFmpegGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Multi-Converter & Remuxer")
        self.root.geometry("700x630")
        
        # Cek ketersediaan ffmpeg.exe
        if not os.path.exists(FFMPEG_PATH):
            messagebox.showerror("Error", f"ffmpeg.exe tidak ditemukan di:\n{FFMPEG_PATH}\n\nPastikan ffmpeg.exe berada di folder yang sama dengan script ini.")
            self.root.destroy()
            return

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_convert = ttk.Frame(self.notebook)
        self.tab_audio = ttk.Frame(self.notebook)  
        self.tab_remux = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_convert, text="Convert Video")
        self.notebook.add(self.tab_audio, text="Convert Audio")  
        self.notebook.add(self.tab_remux, text="Remux Audio+Video")
        
        self.setup_convert_tab()
        self.setup_audio_tab()   
        self.setup_remux_tab()

    # ==================== TAB 1: CONVERT VIDEO ====================
    def setup_convert_tab(self):
        frame_input = ttk.LabelFrame(self.tab_convert, text=" Input / Sumber ")
        frame_input.pack(fill="x", padx=10, pady=5)
        
        self.input_mode = tk.StringVar(value="file")
        ttk.Radiobutton(frame_input, text="Pilih File", variable=self.input_mode, value="file", command=self.toggle_input_mode).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(frame_input, text="Pilih Folder (Batch)", variable=self.input_mode, value="folder", command=self.toggle_input_mode).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.entry_path = ttk.Entry(frame_input, width=55)
        self.entry_path.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.btn_browse = ttk.Button(frame_input, text="Browse", command=self.browse_input)
        self.btn_browse.grid(row=1, column=2, padx=5, pady=5)
        
        frame_input.columnconfigure(0, weight=1)

        frame_settings = ttk.LabelFrame(self.tab_convert, text=" Pengaturan Output ")
        frame_settings.pack(fill="x", padx=10, pady=5)
        
        # Hardware Acceleration
        ttk.Label(frame_settings, text="Hardware Accel:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cb_hw_accel = ttk.Combobox(frame_settings, values=["None (CPU)", "NVIDIA NVENC", "Intel QSV", "AMD AMF"], state="readonly", width=15)
        self.cb_hw_accel.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.cb_hw_accel.set("None (CPU)")
        self.cb_hw_accel.bind("<<ComboboxSelected>>", self.update_codecs)
        
        # Container
        ttk.Label(frame_settings, text="Container:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cb_container = ttk.Combobox(frame_settings, values=["mp4", "mkv", "webm"], state="readonly", width=10)
        self.cb_container.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.cb_container.set("mp4")
        self.cb_container.bind("<<ComboboxSelected>>", self.update_codecs)
        
        # Codec
        ttk.Label(frame_settings, text="Codec Video:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.cb_codec_v = ttk.Combobox(frame_settings, state="readonly", width=10)
        self.cb_codec_v.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_settings, text="Codec Audio:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.cb_codec_a = ttk.Combobox(frame_settings, state="readonly", width=10)
        self.cb_codec_a.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        # Resolution & Orientation
        ttk.Label(frame_settings, text="Resolusi:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.cb_res = ttk.Combobox(frame_settings, values=["480p", "720p", "1080p", "1440p", "2160p"], state="readonly", width=10)
        self.cb_res.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.cb_res.set("1080p")
        
        ttk.Label(frame_settings, text="Orientasi:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.cb_orient = ttk.Combobox(frame_settings, values=["Landscape", "Portrait"], state="readonly", width=10)
        self.cb_orient.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.cb_orient.set("Landscape")
        
        self.update_codecs()

        frame_log = ttk.LabelFrame(self.tab_convert, text=" Status / Log ")
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.txt_log = tk.Text(frame_log, height=8, state="disabled", wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.btn_start_conv = ttk.Button(self.tab_convert, text="MULAI PROSES CONVERT VIDEO", command=self.start_convert_thread)
        self.btn_start_conv.pack(fill="x", padx=10, pady=10)

    def toggle_input_mode(self):
        self.entry_path.delete(0, tk.END)

    def browse_input(self):
        if self.input_mode.get() == "file":
            path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.m4v")])
        else:
            path = filedialog.askdirectory()
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def update_codecs(self, event=None):
        container = self.cb_container.get()
        hw = self.cb_hw_accel.get()
        
        if container == "webm":
            self.cb_codec_v['values'] = ["vp9"]
            self.cb_codec_a['values'] = ["opus"]
            self.cb_codec_v.set("vp9")
            self.cb_codec_a.set("opus")
            return

        if hw == "None (CPU)":
            v_options = ["h264", "h265"] if container == "mp4" else ["h264", "h265", "vp9", "av1"]
        else:
            v_options = ["h264", "h265"]

        a_options = ["aac"] if container == "mp4" else ["aac", "opus"]
        self.cb_codec_v['values'] = v_options
        self.cb_codec_a['values'] = a_options
        self.cb_codec_v.set(v_options[0])
        self.cb_codec_a.set(a_options[0])

    # ==================== FITUR BARU: HARDWARE CHECKER ====================
    def is_hw_encoder_available(self, encoder_name):
        """Fungsi internal untuk mengecek apakah encoder GPU didukung oleh komputer."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Meminta FFmpeg mengecek daftar encoder terpasang
            process = subprocess.run([FFMPEG_PATH, "-encoders"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
            return encoder_name in process.stdout
        except:
            return False

    # ==================== TAB 2: CONVERT AUDIO ====================
    def setup_audio_tab(self):
        frame_input_a = ttk.LabelFrame(self.tab_audio, text=" Input Audio / Sumber ")
        frame_input_a.pack(fill="x", padx=10, pady=5)
        
        self.audio_mode = tk.StringVar(value="file")
        ttk.Radiobutton(frame_input_a, text="Pilih File Audio", variable=self.audio_mode, value="file", command=self.toggle_audio_mode).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(frame_input_a, text="Pilih Folder Audio (Batch)", variable=self.audio_mode, value="folder", command=self.toggle_audio_mode).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.entry_path_a = ttk.Entry(frame_input_a, width=55)
        self.entry_path_a.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.btn_browse_a = ttk.Button(frame_input_a, text="Browse", command=self.browse_audio_input)
        self.btn_browse_a.grid(row=1, column=2, padx=5, pady=5)
        frame_input_a.columnconfigure(0, weight=1)

        frame_settings_a = ttk.LabelFrame(self.tab_audio, text=" Pengaturan Output Audio ")
        frame_settings_a.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_settings_a, text="Format Target:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cb_audio_fmt = ttk.Combobox(frame_settings_a, values=["mp3", "m4a (aac)", "opus", "wav", "flac"], state="readonly", width=15)
        self.cb_audio_fmt.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.cb_audio_fmt.set("mp3")
        
        ttk.Label(frame_settings_a, text="Bitrate / Kualitas:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cb_audio_bitrate = ttk.Combobox(frame_settings_a, values=["128k", "192k", "256k", "320k", "Maksimal/Uncompressed"], state="readonly", width=20)
        self.cb_audio_bitrate.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.cb_audio_bitrate.set("320k")

        frame_log_a = ttk.LabelFrame(self.tab_audio, text=" Status / Log Audio ")
        frame_log_a.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.txt_log_a = tk.Text(frame_log_a, height=10, state="disabled", wrap="word")
        self.txt_log_a.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.btn_start_audio = ttk.Button(self.tab_audio, text="MULAI PROSES CONVERT AUDIO", command=self.start_audio_thread)
        self.btn_start_audio.pack(fill="x", padx=10, pady=10)

    def toggle_audio_mode(self):
        self.entry_path_a.delete(0, tk.END)

    def browse_audio_input(self):
        if self.audio_mode.get() == "file":
            path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac *.m4a *.opus *.flac *.ogg *.wma")])
        else:
            path = filedialog.askdirectory()
        if path:
            self.entry_path_a.delete(0, tk.END)
            self.entry_path_a.insert(0, path)

    def start_audio_thread(self):
        threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        input_path = self.entry_path_a.get()
        if not input_path:
            messagebox.showwarning("Peringatan", "Silakan pilih file atau folder audio terlebih dahulu!")
            return

        self.btn_start_audio.config(state="disabled")
        mode = self.audio_mode.get()
        files_to_process = []
        base_dir = ""
        
        if mode == "file":
            if os.path.isfile(input_path):
                files_to_process.append(input_path)
                base_dir = os.path.dirname(input_path)
        else:
            if os.path.isdir(input_path):
                base_dir = input_path
                for f in os.listdir(input_path):
                    if f.lower().endswith(('.wav', '.mp3', '.aac', '.m4a', '.opus', '.flac', '.ogg', '.wma')):
                        files_to_process.append(os.path.join(input_path, f))

        if not files_to_process:
            self.log("Tidak ada file audio valid untuk diproses.", "audio")
            self.btn_start_audio.config(state="normal")
            return

        output_dir = os.path.join(base_dir, "convert")
        os.makedirs(output_dir, exist_ok=True)

        gui_fmt = self.cb_audio_fmt.get()
        bitrate = self.cb_audio_bitrate.get()
        
        if "m4a" in gui_fmt:
            ext = "m4a"
            codec = "aac"
        else:
            ext = gui_fmt
            codec = "libmp3lame" if gui_fmt == "mp3" else ("libopus" if gui_fmt == "opus" else "pcm_s16le" if gui_fmt == "wav" else "flac")

        self.log(f"--- Memulai Konversi Audio ({len(files_to_process)} file) ---", "audio")
        
        for index, file_path in enumerate(files_to_process, 1):
            filename = os.path.basename(file_path)
            name_without_ext, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name_without_ext}_converted.{ext}")
            
            self.log(f"[{index}/{len(files_to_process)}] Memproses: {filename} -> {ext.upper()}", "audio")
            cmd = [FFMPEG_PATH, "-y", "-i", file_path, "-c:a", codec]
            
            if codec not in ["pcm_s16le", "flac"] and bitrate != "Maksimal/Uncompressed":
                cmd.extend(["-b:a", bitrate])
                
            cmd.append(output_file)
            
            try:
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
                if process.returncode == 0:
                    self.log(f" Sukses!", "audio")
                else:
                    self.log(f" Gagal! Log Error:\n{process.stderr[-200:]}", "audio")
            except Exception as e:
                self.log(f" Error eksekusi: {str(e)}", "audio")

        self.log("--- Semua Proses Audio Selesai! ---", "audio")
        self.btn_start_audio.config(state="normal")
        messagebox.showinfo("Selesai", "Semua proses konversi audio telah selesai!")

    # ==================== TAB 3: REMUX VIDEO + AUDIO ====================
    def setup_remux_tab(self):
        frame_remux = ttk.LabelFrame(self.tab_remux, text=" Pilih Bahan Remux (Audio Lama Dibuang) ")
        frame_remux.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_remux, text="File Video (Hanya Gambar):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_remux_v = ttk.Entry(frame_remux, width=45)
        self.entry_remux_v.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_remux, text="Browse", command=lambda: self.browse_remux("v")).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame_remux, text="File Audio Baru (Suara):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_remux_a = ttk.Entry(frame_remux, width=45)
        self.entry_remux_a.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame_remux, text="Browse", command=lambda: self.browse_remux("a")).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(frame_remux, text="Container Output:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.cb_remux_container = ttk.Combobox(frame_remux, values=["mp4", "mkv", "webm"], state="readonly", width=10)
        self.cb_remux_container.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.cb_remux_container.set("mp4")

        frame_log_r = ttk.LabelFrame(self.tab_remux, text=" Status / Log Remux ")
        frame_log_r.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.txt_log_r = tk.Text(frame_log_r, height=10, state="disabled", wrap="word")
        self.txt_log_r.pack(fill="both", expand=True, padx=5, pady=5)

        self.btn_start_remux = ttk.Button(self.tab_remux, text="MULAI PROSES REMUX (Direct Copy)", command=self.start_remux_thread)
        self.btn_start_remux.pack(fill="x", padx=10, pady=10)

    def browse_remux(self, type_file):
        if type_file == "v":
            path = filedialog.askopenfilename(title="Pilih File Video", filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.webm *.h264 *.h265")])
            if path:
                self.entry_remux_v.delete(0, tk.END)
                self.entry_remux_v.insert(0, path)
        else:
            path = filedialog.askopenfilename(title="Pilih File Audio", filetypes=[("Audio Files", "*.mp3 *.m4a *.aac *.opus *.ogg *.wav *.flac")])
            if path:
                self.entry_remux_a.delete(0, tk.END)
                self.entry_remux_a.insert(0, path)

    # ==================== LOGIC UTILITY ====================
    def log(self, text, tab="convert"):
        if tab == "convert":
            target = self.txt_log
        elif tab == "audio":
            target = self.txt_log_a
        else:
            target = self.txt_log_r
            
        target.config(state="normal")
        target.insert(tk.END, text + "\n")
        target.see(tk.END)
        target.config(state="disabled")

    def start_convert_thread(self):
        threading.Thread(target=self.process_convert, daemon=True).start()

    def process_convert(self):
        input_path = self.entry_path.get()
        if not input_path:
            messagebox.showwarning("Peringatan", "Silakan pilih file atau folder sumber terlebih dahulu!")
            return

        self.btn_start_conv.config(state="disabled")
        mode = self.input_mode.get()
        files_to_process = []
        base_dir = ""
        
        if mode == "file":
            if os.path.isfile(input_path):
                files_to_process.append(input_path)
                base_dir = os.path.dirname(input_path)
        else:
            if os.path.isdir(input_path):
                base_dir = input_path
                for f in os.listdir(input_path):
                    if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.m4v')):
                        files_to_process.append(os.path.join(input_path, f))

        if not files_to_process:
            self.log("Tidak ada file video valid untuk diproses.")
            self.btn_start_conv.config(state="normal")
            return

        output_dir = os.path.join(base_dir, "convert")
        os.makedirs(output_dir, exist_ok=True)

        hw_selection = self.cb_hw_accel.get()
        container = self.cb_container.get()
        gui_codec_v = self.cb_codec_v.get()
        codec_a = "libopus" if self.cb_codec_a.get() == "opus" else "aac"

        # Tentukan target codec berdasarkan hardware pilihan user
        target_encoder = ""
        if container != "webm" and hw_selection != "None (CPU)":
            if hw_selection == "Intel QSV":
                target_encoder = "h264_qsv" if gui_codec_v == "h264" else "hevc_qsv"
            elif hw_selection == "NVIDIA NVENC":
                target_encoder = "h264_nvenc" if gui_codec_v == "h264" else "hevc_nvenc"
            elif hw_selection == "AMD AMF":
                target_encoder = "h264_amf" if gui_codec_v == "h264" else "hevc_amf"

        # --- VALIDASI HARDWARE ACCELERATION & AUTO FALLBACK ---
        if target_encoder:
            if not self.is_hw_encoder_available(target_encoder):
                # Buat pop-up peringatan interaktif
                messagebox.showwarning(
                    "Hardware Tidak Mendukung", 
                    f"Komputer Anda tidak mendukung encoder '{target_encoder}' dari grafis {hw_selection}.\n\n"
                    f"Sistem secara otomatis mengalihkan (FALLBACK) proses ini ke 'None (CPU)' demi mencegah error."
                )
                # Ubah status GUI ke CPU secara langsung
                self.cb_hw_accel.set("None (CPU)")
                hw_selection = "None (CPU)"

        # Memperbaiki filter resolusi & format piksel warna universal
        res = self.cb_res.get()
        orient = self.cb_orient.get()
        res_map = {"480p": (854, 480), "720p": (1280, 720), "1080p": (1920, 1080), "1440p": (2560, 1440), "2160p": (3840, 2160)}
        w, h = res_map[res]
        if orient == "Portrait": 
            w, h = h, w
        video_filters = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"

        self.log(f"--- Memulai Konversi ({len(files_to_process)} file) ---")
        
        for index, file_path in enumerate(files_to_process, 1):
            filename = os.path.basename(file_path)
            name_without_ext, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name_without_ext}_converted.{container}")
            
            self.log(f"[{index}/{len(files_to_process)}] Memproses: {filename}")
            cmd = [FFMPEG_PATH, "-y"]
            
            if hw_selection == "NVIDIA NVENC" and container != "webm": 
                cmd.extend(["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"])
                
            cmd.extend(["-i", file_path])
            
            if container == "webm":
                cmd.extend(["-c:v", "libvpx-vp9"])
            else:
                if hw_selection == "Intel QSV":
                    codec_v = "h264_qsv" if gui_codec_v == "h264" else "hevc_qsv"
                    cmd.extend(["-c:v", codec_v, "-global_quality", "23"])
                elif hw_selection == "NVIDIA NVENC":
                    codec_v = "h264_nvenc" if gui_codec_v == "h264" else "hevc_nvenc"
                    cmd.extend(["-c:v", codec_v, "-cq", "23"])
                elif hw_selection == "AMD AMF":
                    codec_v = "h264_amf" if gui_codec_v == "h264" else "hevc_amf"
                    cmd.extend(["-c:v", codec_v])
                else:
                    codec_v = "libx264" if gui_codec_v == "h264" else "libx265"
                    cmd.extend(["-c:v", codec_v, "-crf", "23"])
                    
            cmd.extend(["-c:a", codec_a, "-vf", video_filters, output_file])
            
            try:
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
                if process.returncode == 0: 
                    self.log(f" Sukses!")
                else: 
                    self.log(f" Gagal! Log Error:\n{process.stderr[-250:]}")
            except Exception as e:
                self.log(f" Error eksekusi: {str(e)}")

        self.log("--- Semua Proses Selesai! ---")
        self.btn_start_conv.config(state="normal")
        messagebox.showinfo("Selesai", "Semua proses konversi video telah selesai!")

    def start_remux_thread(self):
        threading.Thread(target=self.process_remux, daemon=True).start()

    def process_remux(self):
        v_path = self.entry_remux_v.get()
        a_path = self.entry_remux_a.get()
        if not v_path or not a_path:
            messagebox.showwarning("Peringatan", "File Video dan Audio harus diisi!")
            return
            
        self.btn_start_remux.config(state="disabled")
        base_dir = os.path.dirname(v_path)
        output_dir = os.path.join(base_dir, "convert")
        os.makedirs(output_dir, exist_ok=True)
        
        name_without_ext, _ = os.path.splitext(os.path.basename(v_path))
        container = self.cb_remux_container.get()
        output_file = os.path.join(output_dir, f"{name_without_ext}_remux_new_audio.{container}")
        
        self.log(f"Memulai Remuxing (Hapus Audio Lama + Pasang Audio Baru)...", "remux")
        cmd = [
            FFMPEG_PATH, "-y", "-i", v_path, "-i", a_path,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "copy", "-shortest", output_file
        ]
        
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
            if process.returncode == 0:
                self.log(f" Sukses! Audio lama dibuang & audio baru disatukan.\nTersimpan di: {output_file}", "remux")
                messagebox.showinfo("Selesai", "Remux (Ganti Audio) berhasil diselesaikan!")
            else:
                self.log(f" Gagal! Error:\n{process.stderr[-200:]}", "remux")
        except Exception as e:
            self.log(f" Error eksekusi: {str(e)}", "remux")
            
        self.btn_start_remux.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = FFmpegGUI(root)
    root.mainloop()
