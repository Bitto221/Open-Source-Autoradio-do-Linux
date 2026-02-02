import subprocess
import subprocess
import time
import sys

WINDOW_TITLE = "YouTube Music"

def is_running():
    result = subprocess.run(
        ["wmctrl", "-l"],
        stdout=subprocess.PIPE,
        text=True
    )
    return WINDOW_TITLE.lower() in result.stdout.lower()

def focus_window():
    subprocess.run(["wmctrl", "-a", WINDOW_TITLE])

def start_youtube():
    subprocess.Popen([
        "chromium-browser",
        "--app=https://music.youtube.com",
        "--window-size=800,480",
        "--disable-infobars",
        "--no-first-run"
    ])

if __name__ == "__main__":
    if is_running():
        focus_window()
    else:
        start_youtube()
