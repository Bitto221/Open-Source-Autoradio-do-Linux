import subprocess

def open_bluetooth_settings():
    subprocess.Popen([
        "gnome-control-center",
        "bluetooth"
    ])

if __name__ == "__main__":
    open_bluetooth_settings()