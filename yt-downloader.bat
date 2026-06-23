@echo off
setlocal enabledelayedexpansion
set "OUTDIR=%USERPROFILE%\Downloads"

:: Check dependencies
where yt-dlp >nul 2>&1 || (
    echo [ERROR] yt-dlp not found.
    echo Download from: https://github.com/yt-dlp/yt-dlp
    pause
    exit /b 1
)

where mpv >nul 2>&1 || (
    echo [ERROR] mpv player not found.
    echo Download from: https://mpv.io/installation/
    pause
    exit /b 1
)

where ffmpeg >nul 2>&1 || (
    echo [ERROR] FFmpeg not found.
    echo Required for audio conversion and video merging.
    echo Download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

:MENU
cls
set "URL="
set "CHOICE="
echo ==============================
echo       YOUTUBE DOWNLOADER
echo ==============================
set /p "URL=Enter YouTube URL: "
if "%URL%"=="" (
    echo [ERROR] URL cannot be empty.
    pause
    goto MENU
)

echo [1] Download Video (Best Quality)
echo [2] Download Audio (MP3)
echo [3] Select Video Format
echo [4] Stream Video
echo [0] Exit
echo ==============================
set /p "CHOICE=Enter choice [0-4]: "

if "%CHOICE%"=="1" goto BEST_VIDEO
if "%CHOICE%"=="2" goto AUDIO
if "%CHOICE%"=="3" goto SELECT_FORMAT
if "%CHOICE%"=="4" goto PLAY
if "%CHOICE%"=="0" goto EXIT

echo.
echo Invalid choice!
pause
goto MENU

:BEST_VIDEO
cls
echo.
echo Downloading best quality video...
yt-dlp -f "bestvideo+bestaudio" --merge-output-format mkv -o "%OUTDIR%\%%(title)s.%%(ext)s" "%URL%"
pause
goto MENU

:AUDIO
cls
echo.
echo Downloading best audio as MP3...
yt-dlp -f "bestaudio[acodec^=mp4a]" --extract-audio --audio-format mp3 --audio-quality 0 -o "%OUTDIR%\%%(title)s.%%(ext)s" "%URL%"
pause
goto MENU

:SELECT_FORMAT
cls
echo.
echo Available formats:
yt-dlp -F "%URL%"
echo.

set "FORMAT="
set /p "FORMAT=Enter format code (e.g., 136): "
if "%FORMAT%"=="" (
    echo [ERROR] Format code required.
    pause
    goto SELECT_FORMAT
)

echo.
echo Downloading format %FORMAT% + bestaudio(m4a)...
yt-dlp -f "%FORMAT%+bestaudio[acodec^=mp4a]" --merge-output-format mkv -o "%OUTDIR%\%%(title)s.%%(ext)s" "%URL%"
pause
goto MENU

:PLAY
cls
echo ==============================
echo         STREAM OPTIONS
echo ==============================
echo [1] Best Quality (Auto)
echo [2] 1080p
echo [3] 720p
echo [4] 480p
echo [5] 360p
echo [0] Back to Main Menu
echo ==============================
set "RES="
set /p "RES=Select quality [0-5]: "

set "MPV_FLAGS=--hwdec=auto-safe"

if "%RES%"=="1" (
    echo Streaming best quality...
    mpv %MPV_FLAGS% "%URL%"
    goto PLAY
)
if "%RES%"=="2" (
    echo Streaming 1080p...
    mpv %MPV_FLAGS% --ytdl-format="bestvideo[height<=1080]+bestaudio/best[height<=1080]" "%URL%"
    goto PLAY
)
if "%RES%"=="3" (
    echo Streaming 720p...
    mpv %MPV_FLAGS% --ytdl-format="bestvideo[height<=720]+bestaudio/best[height<=720]" "%URL%"
    goto PLAY
)
if "%RES%"=="4" (
    echo Streaming 480p...
    mpv %MPV_FLAGS% --ytdl-format="bestvideo[height<=480]+bestaudio/best[height<=480]" "%URL%"
    goto PLAY
)
if "%RES%"=="5" (
    echo Streaming 360p...
    mpv %MPV_FLAGS% --ytdl-format="bestvideo[height<=360]+bestaudio/best[height<=360]" "%URL%"
    goto PLAY
)
if "%RES%"=="0" goto MENU

echo.
echo Invalid choice!
pause
goto PLAY

:EXIT
echo.
exit /b
