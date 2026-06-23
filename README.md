# YT-Downloader

A lightweight Python GUI for `yt-dlp` designed for easy video and audio downloading.

## 📁 Project Structure

Place all required executable files in the root directory as shown below:

```text
yt-downloader/
├── ffmpeg.exe
├── mpv.exe
├── yt-dlp.exe
├── yt-downloader.bat
└── yt-downloader.pyw
```

## 🚀 Prerequisites

Before running the application, ensure you have the following components:

1. **Python 3.x** installed on your system.
2. **External Binaries** placed in the project folder:
   * `yt-dlp.exe`: The core download engine.
   * `ffmpeg.exe`: Required for merging high-quality video and audio streams.
   * `mpv.exe`: Optional, used for video preview/playback functionality.

## 🛠️ How to Run

You can launch the application in two ways:

1. **Via Batch File (Recommended):**
   Double-click `yt-downloader.bat` to launch the GUI without leaving a background command prompt window open.

2. **Via Python:**
   Double-click `yt-downloader.pyw` or run it from your terminal:
   ```bash
   python yt-downloader.pyw
   ```

## ✨ Features

* Simple and clean Graphical User Interface (GUI).
* Supports high-quality video and audio extraction via `yt-dlp`.
* Automatic stream merging using `ffmpeg`.
* Background execution using the `.pyw` extension to hide the console terminal.
