import subprocess

def open_youtube():
    subprocess.Popen([
        "chromium-browser",
        "--app=https://www.youtube.com/",
        "--window-size=800,480",
        "--disable-infobars",
        "--no-first-run",
        "--disable-session-crashed-bubble"
    ])

open_youtube()