from app_launcher import app_run_or_focus

WINDOW_TITLE = "Web"

COMMAND = [
    "chromium-browser",
    "--app=https://google.com",
    "--window-size=800,480",
    "--disable-infobars",
    "--no-first-run",
    "--disable-session-crashed-bubble"
]


def launch():
    app_run_or_focus(WINDOW_TITLE, COMMAND)


if __name__ == "__main__":
    launch()

# hotový kod
# verze 1.2
