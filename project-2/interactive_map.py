import folium

avg_lat = merged_stats['lat'].mean()
avg_lon = merged_stats['lon'].mean()
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)

# Color palette
colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue', 'darkgreen', 'pink', 'gray']

# Plot each cluster
for i, row in merged_stats.iterrows():
    cluster_id = int(row['cluster'])
    label = f"Cluster {cluster_id}<br>Time: {row['total_duration']/3600:.2f} hrs<br>Visits: {int(row['count'])}"
    folium.CircleMarker(
        location=(row['lat'], row['lon']),
        radius=8,
        popup=folium.Popup(label, max_width=300),
        color=colors[cluster_id % len(colors)],
        fill=True,
        fill_color=colors[cluster_id % len(colors)],
        fill_opacity=0.7
    ).add_to(m)

# Display the map
m.save("cluster_map.html")
