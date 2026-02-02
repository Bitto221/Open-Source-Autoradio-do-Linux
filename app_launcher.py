import subprocess

def app_run_or_focus(window_title, start_command):
    result = subprocess.run(
        ["wmctrl", "-l"],
        stdout=subprocess.PIPE,
        text=True
    )

    if window_title.lower() in result.stdout.lower():
        subprocess.run(["wmctrl", "-a", window_title])
    else:
        subprocess.Popen(start_command)
import subprocess

def app_run_or_focus(window_title, start_command):
    result = subprocess.run(
        ["wmctrl", "-l"],
        stdout=subprocess.PIPE,
        text=True
    )

    if window_title.lower() in result.stdout.lower():
        subprocess.run(["wmctrl", "-a", window_title])
    else:
        subprocess.Popen(start_command)
