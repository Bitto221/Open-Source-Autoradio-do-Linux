import folium

# centrum (Praha jako test)
m = folium.Map(location=[50.0755, 14.4378], zoom_start=13)

m.save("map.html")
print("Mapa vytvořena: map.html")