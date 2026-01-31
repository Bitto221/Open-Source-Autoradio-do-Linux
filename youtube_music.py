import subprocess

def open_youtube_music():
    subprocess.Popen([
        "chromium-browser",
        "--app=https://music.youtube.com",
        "--window-size=800,480",
        "--disable-infobars",
        "--no-first-run"
    ])

open_youtube_music()   # ← TOHLE TAM MUSÍ BÝT