from app_launcher import app_run_or_focus

WINDOW_TITLE = "Web"

COMMAND = [
    "chromium-browser",
    "--app=https://google.com",
    "--window-size=800,480",
    "--disable-infobars",
    "--no-first-run"
    "--disable-session-crashed-bubble"
]

app_run_or_focus(WINDOW_TITLE, COMMAND)
# hotový kod
# verze 1.1