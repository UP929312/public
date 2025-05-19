import osmnx as ox
import folium
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex, LogNorm
from pre_parsed import DATA

# --- SETTINGS ---
CITY = "Brighton and Hove, UK"
IGNORE_ZERO_FREQUENCY = True  # Ignore streets with zero frequency

# --- LOAD GRAPH AND FILTER STREETS ---
print(f"Downloading map data for {CITY}...")
G = ox.graph_from_place(CITY, network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False)
print("Map data downloaded.")

# --- PREPARE DATA ---
for edge in edges['name']:
    if isinstance(edge, str) and edge not in DATA.keys() and IGNORE_ZERO_FREQUENCY:
        DATA[edge] = 0  # Assign a default value of 0 if the street is not in DATA

# Find missing street names ====================
# map_street_names = set()

# for name in edges["name"].dropna():
#     if isinstance(name, list):
#         map_street_names.update(n.lower() for n in name)
#     elif isinstance(name, str):
#         map_street_names.add(name.lower())
# missing_streets = [street for street in DATA if street.lower() not in map_street_names]
# for street in missing_streets:
#     print(f"Warning: {street} not found in map data. It will be ignored.")
# ==============================================

# Match streets in your data
matched_edges = edges[edges['name'].isin(DATA.keys())].copy()

# Assign frequencies to edges
matched_edges['frequency'] = matched_edges['name'].map(DATA)

# Normalize frequencies for colormap
norm = LogNorm(vmin=max(min(DATA.values()), 1), vmax=max(DATA.values()))
cmap = plt.cm.get_cmap('RdYlGn_r')  # Green = low, Red = high

# Add a new row, colour which is set to a logerithmic scale
matched_edges['color'] = matched_edges['frequency'].apply(lambda x: to_hex(cmap(norm(x))))

# --- CREATE FOLIUM MAP ---
# Center map on the city
lat, lon = ox.geocode(CITY)
m = folium.Map(
    location=[lat-0.009, lon+0.02],
    zoom_start=13,
    tiles="CartoDB positron",  #, attr='© OpenStreetMap contributors © CARTO')  # CartoDB dark_matter, Stamen Toner Lite, OpenStreetMap, (default), CartoDB positron
)

# Draw colored streets
for _, row in matched_edges.iterrows():
    freq = DATA.get(row['name'], 0)
    lines = row.geometry.geoms if row.geometry.geom_type == 'MultiLineString' else [row.geometry]

    for line in lines:
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in line.coords],
            tooltip=f"{row['name']}: {row['frequency']}",
            color=row['color'] if freq > 0 else "#999999",  # Light gray for zero frequency
            weight=5 if freq > 0 else 2,
            opacity=0.8 if freq > 0 else 0.2,
        ).add_to(m)

# --- SAVE MAP ---
output_file = "city_street_heatmap.html"
m.save(output_file)
print(f"Map saved to {output_file}")