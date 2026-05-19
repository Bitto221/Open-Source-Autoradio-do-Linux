#!/usr/bin/env python3
"""
Spouštěč navigace – stačí spustit: python3 navigace.py
"""

import subprocess
import threading
import time
import sys
import os
import socket
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ── KONFIGURACE ───────────────────────────────────────────────────────────────
OSRM_IMAGE  = "ghcr.io/project-osrm/osrm-backend"
OSRM_DATA   = os.path.expanduser("~/osrm-data")
OSRM_FILE   = "czech-republic-latest.osrm"
OSRM_PORT   = 5000
SERVER_PORT = 8080
CACHE_DIR   = "tile_cache"
URL         = f"http://localhost:{SERVER_PORT}/navigace.html"

TILE_PROVIDERS = [
    "https://{sub}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "https://tile.openstreetmap.de/{z}/{x}/{y}.png",
    "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── TERMINAL OUTPUT ───────────────────────────────────────────────────────────
CYAN  = "\033[96m"
GREEN = "\033[92m"
RED   = "\033[91m"
GRAY  = "\033[90m"
BOLD  = "\033[1m"
RST   = "\033[0m"

def log(msg, color=GRAY):     print(f"  {color}{msg}{RST}")
def ok(msg):                  print(f"  {GREEN}✓{RST}  {msg}")
def err(msg):                 print(f"  {RED}✗{RST}  {msg}")
def header():
    print()
    print(f"  {CYAN}{BOLD}╔══════════════════════════════════╗{RST}")
    print(f"  {CYAN}{BOLD}║   🗺   NAVCZ  –  Offline mapa    ║{RST}")
    print(f"  {CYAN}{BOLD}╚══════════════════════════════════╝{RST}")
    print()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def wait_for_port(port, label, timeout=30):
    log(f"Čekám na {label}…")
    for _ in range(timeout * 2):
        if port_open(port):
            ok(f"{label} připraven")
            return True
        time.sleep(0.5)
    err(f"{label} se nespustil včas")
    return False

# ── OSRM ──────────────────────────────────────────────────────────────────────
def start_osrm():
    if port_open(OSRM_PORT):
        ok("OSRM již běží")
        return True

    log("Spouštím OSRM…")
    cmd = ["docker","run","-d","-p",f"{OSRM_PORT}:{OSRM_PORT}",
           "-v",f"{OSRM_DATA}:/data", OSRM_IMAGE,
           "osrm-routed","--algorithm","mld",f"/data/{OSRM_FILE}"]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if "permission denied" in r.stderr.lower():
        r = subprocess.run(["sudo"]+cmd, capture_output=True, text=True)
    if r.returncode != 0:
        err(f"OSRM se nepodařilo spustit: {r.stderr.strip()}")
        return False
    return wait_for_port(OSRM_PORT, "OSRM")

# ── HTTP SERVER ────────────────────────────────────────────────────────────────
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/osrm/"):
            self._proxy_json(f"http://127.0.0.1:{OSRM_PORT}" + self.path[len("/osrm"):])
            return
        if self.path.startswith("/tiles/"):
            parts = self.path[len("/tiles/"):].strip("/").split("/")
            if len(parts) == 3:
                z, x, y_png = parts
                self._serve_tile(z, x, y_png.replace(".png",""))
                return
        super().do_GET()

    def _serve_tile(self, z, x, y):
        cp = os.path.join(SCRIPT_DIR, CACHE_DIR, z, x, f"{y}.png")
        if os.path.exists(cp):
            with open(cp,"rb") as f: self._send_image(f.read())
            return
        sub = "abc"[int(x)%3]
        for tpl in TILE_PROVIDERS:
            url = tpl.format(sub=sub,z=z,x=x,y=y)
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; NavigaceCZ/1.0)",
                    "Referer":    "https://www.openstreetmap.org/",
                    "Accept":     "image/png,image/*",
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                os.makedirs(os.path.join(SCRIPT_DIR, CACHE_DIR, z, x), exist_ok=True)
                with open(cp,"wb") as f: f.write(data)
                self._send_image(data)
                return
            except Exception: continue
        self.send_response(204); self.end_headers()

    def _send_image(self, data):
        self.send_response(200)
        self.send_header("Content-Type","image/png")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Cache-Control","public, max-age=2592000")
        self.end_headers(); self.wfile.write(data)

    def _proxy_json(self, url):
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=15) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*")
            self.end_headers(); self.wfile.write(data)
        except Exception as e:
            self.send_response(502); self.send_header("Content-Type","text/plain")
            self.end_headers(); self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args): pass

def start_server():
    os.makedirs(os.path.join(SCRIPT_DIR, CACHE_DIR), exist_ok=True)
    os.chdir(SCRIPT_DIR)
    httpd = HTTPServer(("", SERVER_PORT), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

# ── CHROMIUM KIOSK ────────────────────────────────────────────────────────────
def open_chromium(url):
    # Hledáme dostupný prohlížeč
    browsers = ["chromium-browser","chromium","google-chrome","google-chrome-stable"]
    for b in browsers:
        r = subprocess.run(["which", b], capture_output=True, text=True)
        if r.returncode == 0:
            browser = r.stdout.strip()
            log(f"Otevírám {b} v kiosk módu…")
            subprocess.Popen([
                browser,
                "--app=" + url,          # bez lišty, bez záložek
                "--window-size=800,480",
                "--disable-infobars",
                "--no-first-run",
                "--disable-translate",
                "--disable-features=TranslateUI",
                "--no-default-browser-check",
            ])
            return
    err("Chromium/Chrome nenalezen, otevírám výchozí prohlížeč")
    import webbrowser
    webbrowser.open(url)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    header()

    if not start_osrm():
        input("\n  Stiskni Enter pro ukončení…")
        sys.exit(1)

    if port_open(SERVER_PORT):
        ok(f"HTTP server již běží (:{SERVER_PORT})")
    else:
        log("Spouštím HTTP server…")
        start_server()
        time.sleep(0.3)
        ok(f"HTTP server připraven (:{SERVER_PORT})")

    time.sleep(0.5)
    open_chromium(URL)

    print()
    print(f"  {BOLD}Navigace:{RST}  {CYAN}{URL}{RST}")
    print(f"  {GRAY}Zastav:    Ctrl+C{RST}")
    print()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n  {GRAY}Ukončuji…{RST}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
