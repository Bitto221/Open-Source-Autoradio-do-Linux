from app_launcher import app_run_or_focus

WINDOW_TITLE = "Navit"

COMMAND = ["navit"]


def launch():
    app_run_or_focus(WINDOW_TITLE, COMMAND)


if __name__ == "__main__":
    launch()

# hotový kod
# verze 3 - Navit místo GNOME Maps (čte GPS přímo z gpsd, žádné
# GeoClue2/Avahi/D-Bus - viz README, sekce Navigace)
