import subprocess

def open_spotube():
    subprocess.Popen([
        "flatpak",
        "run",
        "com.github.KRTirtho.Spotube",
        "--window-size=800,480"
    ])

open_spotube()
