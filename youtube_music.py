import subprocess

def open_youtube_music():
    subprocess.Popen([
        "chromium-browser",
        "--app=https://music.youtube.com",
        "--start-maximized",
        "--disable-infobars",
        "--no-first-run"
    ])

open_youtube_music()   # ← TOHLE TAM MUSÍ BÝT