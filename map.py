import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView


html = """
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8"/>

<link rel="stylesheet"
 href="https://unpkg.com/leaflet/dist/leaflet.css"/>

<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>

html, body {
    margin:0;
    width:100%;
    height:100%;
    background:black;
}

#map {
    width:100%;
    height:100%;
}

</style>

</head>

<body>

<div id="map"></div>

<script>

var map = L.map('map').setView([50.0755, 14.4378], 10);

L.tileLayer(
'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
{
    maxZoom:19
}
).addTo(map);

</script>

</body>
</html>
"""


class Maps(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maps")
        self.setFixedSize(800, 480)

        self.browser = QWebEngineView()
        self.browser.setHtml(html)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        self.setLayout(layout)


app = QApplication(sys.argv)

window = Maps()
window.show()

sys.exit(app.exec_())