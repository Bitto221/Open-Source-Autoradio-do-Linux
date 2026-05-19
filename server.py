#!/usr/bin/env python3
"""
Server pro offline navigaci s tile proxy + lokální tile cache.
Spuštění: python3 server.py
Pak otevři: http://localhost:8080/navigace.html
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import os

OSRM = "http://127.0.0.1:5000"
PORT  = 8080
CACHE_DIR = "tile_cache"

# Více tile providerů – zkusí je postupně pokud jeden selže
TILE_PROVIDERS = [
    "https://{sub}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "https://tile.openstreetmap.de/{z}/{x}/{y}.png",
    "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png",
]

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/osrm/"):
            self._proxy_json(OSRM + self.path[len("/osrm"):])
            return

        if self.path.startswith("/tiles/"):
            parts = self.path[len("/tiles/"):].strip("/").split("/")
            if len(parts) == 3:
                z, x, y_png = parts
                y = y_png.replace(".png", "")
                self._serve_tile(z, x, y)
                return

        super().do_GET()

    def _serve_tile(self, z, x, y):
        # Zkus lokální cache
        cache_path = os.path.join(CACHE_DIR, z, x, f"{y}.png")
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
            self._send_image(data)
            return

        # Stáhni z providerů
        sub = "abc"[int(x) % 3]
        for tpl in TILE_PROVIDERS:
            url = tpl.format(sub=sub, z=z, x=x, y=y)
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; NavigaceCZ/1.0; +http://localhost)",
                    "Referer":    "https://www.openstreetmap.org/",
                    "Accept":     "image/png,image/*",
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()

                # Ulož do cache
                os.makedirs(os.path.join(CACHE_DIR, z, x), exist_ok=True)
                with open(cache_path, "wb") as f:
                    f.write(data)

                self._send_image(data)
                return
            except Exception as e:
                print(f"  Provider selhal ({url[:50]}...): {e}")
                continue

        # Všichni selhali – vrať prázdnou dlaždici
        self.send_response(204)
        self.end_headers()

    def _send_image(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=2592000")  # 30 dní
        self.end_headers()
        self.wfile.write(data)

    def _proxy_json(self, url):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "NavigaceCZ/1.0",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        if "502" in str(args):
            print(f"  ERR {args}")

if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cached = sum(len(fs) for _, _, fs in os.walk(CACHE_DIR))
    print(f"\n  Server běží:  http://localhost:{PORT}")
    print(f"  Otevři:       http://localhost:{PORT}/navigace.html")
    print(f"  Tile cache:   ./{CACHE_DIR}/ ({cached} dlaždic uloženo)")
    print(f"  Zastav:       Ctrl+C\n")
    HTTPServer(("", PORT), Handler).serve_forever()
