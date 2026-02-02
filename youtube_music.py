from app_launcher import app_run_or_focus

WINDOW_TITLE = "YouTube Music"

COMMAND = [
    "chromium-browser",
    "--app=https://music.youtube.com",
    "--window-size=800,480",
    "--disable-infobars",
    "--no-first-run"
]

app_run_or_focus(WINDOW_TITLE, COMMAND)