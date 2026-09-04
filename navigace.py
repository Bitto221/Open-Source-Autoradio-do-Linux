from app_launcher import app_run_or_focus

WINDOW_TITLE = "Maps"

COMMAND = ["gnome-maps"]


def launch():
    app_run_or_focus(WINDOW_TITLE, COMMAND)


if __name__ == "__main__":
    launch()

# hotový kod
# verze 2
