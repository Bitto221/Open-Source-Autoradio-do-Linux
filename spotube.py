import subprocess

def open_spotube():
    subprocess.Popen([
        "flatpak",
        "run",
        "com.github.KRTirtho.Spotube"
    ])

open_spotube()
