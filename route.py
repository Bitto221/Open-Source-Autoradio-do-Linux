import requests
import json

# start (Praha)
start_lat, start_lon = 50.0755, 14.4378

# cíl (trochu vedle)
end_lat, end_lon = 50.0900, 14.4200

url = f"http://localhost:5000/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"

response = requests.get(url)
data = response.json()

coords = data["routes"][0]["geometry"]["coordinates"]

# uložíme trasu pro mapu
with open("route.json", "w") as f:
    json.dump(coords, f)

print("Trasa uložená do route.json")