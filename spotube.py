from app_launcher import app_run_or_focus

WINDOW_TITLE = "YouTube"

COMMAND = [
    "flatpak",
    "run",
    "com.github.KRTirtho.Spotube",
    "--window-size=800,480"
]

app_run_or_focus(WINDOW_TITLE, COMMAND)
# hotový kod
# verze 3.4 