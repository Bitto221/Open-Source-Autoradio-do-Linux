from app_launcher import app_run_or_focus

WINDOW_TITLE = "welle.io"

COMMAND = ["welle-io"]


def launch():
    app_run_or_focus(WINDOW_TITLE, COMMAND)


if __name__ == "__main__":
    launch()

# hotový kod
# verze 4 - zpět na spouštěč skutečné aplikace welle-io (nahrazuje
# krátce používaný vlastní modul dab_radio.py nad welle-cli) - díky
# app_run_or_focus() teď navíc naskočí fullscreen bez GNOME horní lišty
