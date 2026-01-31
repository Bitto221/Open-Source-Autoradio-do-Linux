import subprocess

def open_bluetooth_settings():
    subprocess.Popen([
        "gnome-control-center",
        "bluetooth",
        "--window-size=800,480"
    ])

if __name__ == "__main__":
    open_bluetooth_settings()