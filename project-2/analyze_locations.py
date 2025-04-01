import json
import pandas as pd
from datetime import datetime
from sklearn.cluster import DBSCAN
import numpy as np
import requests
from geopy.distance import geodesic

# ---- CONFIG ----
FOURSQUARE_API_KEY = "fsq3Cvan1HKVgaVmV2/PzJfEZg7YEfLZLzyPaVy0RnmRLpU="  # Replace with your real key
USE_FOURSQUARE = True  # Disable API calls by setting this to False
MERGE_DISTANCE_METERS = 250  # Merge radius for nearby clusters

# ---- Step 1: Load Location History ----
with open("location_history.json") as f:
    data = json.load(f)

records = data["Location History"]
locations = []

for time_str, coord_str in records:
    try:
        lat_str, lon_str = coord_str.split(", ")

        # Remove "± X meters" if present
        lat_clean = lat_str.split("\u00b1")[0].strip()
        lon_clean = lon_str.split("\u00b1")[0].strip()

        lat = float(lat_clean)
        lon = float(lon_clean)
        time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S UTC")
        locations.append({"time": time, "latitude": lat, "longitude": lon})
    except Exception as e:
        print(f"Skipping malformed record: {coord_str} ({e})")

df = pd.DataFrame(locations)

# ---- Step 2: Cluster Locations ----
kms_per_radian = 6371.0088
epsilon = 0.1 / kms_per_radian  # ~100 meters

coords = df[["latitude", "longitude"]].values
db = DBSCAN(eps=epsilon, min_samples=5, algorithm='ball_tree', metric='haversine')
df['cluster'] = db.fit_predict(np.radians(coords))

# ---- Step 3: Aggregate Time at Clusters ----
df = df.sort_values("time")
df['next_time'] = df['time'].shift(-1)
df['duration'] = (df['next_time'] - df['time']).dt.total_seconds()

grouped = df.groupby('cluster').agg({
    'latitude': 'mean',
    'longitude': 'mean',
    'duration': 'sum',
    'time': ['count', 'min', 'max']
}).reset_index()
grouped.columns = ['cluster', 'lat', 'lon', 'total_duration', 'count', 'start_time', 'end_time']
grouped_filtered = grouped[grouped['cluster'] != -1]

# ---- Step 4: Merge Close Clusters ----
def merge_close_clusters(df_clusters, merge_distance_meters):
    merged_ids = {}
    cluster_centers = df_clusters[["cluster", "lat", "lon"]].values
    next_cluster_id = 0
    assigned = {}

    for i, (cluster_i, lat_i, lon_i) in enumerate(cluster_centers):
        if cluster_i in assigned:
            continue
        merged_ids[cluster_i] = next_cluster_id
        assigned[cluster_i] = True

        for j, (cluster_j, lat_j, lon_j) in enumerate(cluster_centers):
            if cluster_j in assigned:
                continue
            dist = geodesic((lat_i, lon_i), (lat_j, lon_j)).meters
            if dist <= merge_distance_meters:
                merged_ids[cluster_j] = next_cluster_id
                assigned[cluster_j] = True

        next_cluster_id += 1

    df_clusters = df_clusters.copy()
    df_clusters["merged_cluster"] = df_clusters["cluster"].map(merged_ids)
    return df_clusters, merged_ids

grouped_merged, merge_map = merge_close_clusters(grouped_filtered, MERGE_DISTANCE_METERS)
df["merged_cluster"] = df["cluster"].map(merge_map).fillna(-1).astype(int)

merged_stats = df[df["merged_cluster"] != -1].groupby("merged_cluster").agg({
    'latitude': 'mean',
    'longitude': 'mean',
    'duration': 'sum',
    'time': ['count', 'min', 'max']
}).reset_index()
merged_stats.columns = ['cluster', 'lat', 'lon', 'total_duration', 'count', 'start_time', 'end_time']

# ---- Step 5: Print Cluster Summary ----
print("\n--- Merged Significant Location Clusters ---\n")
for _, row in merged_stats.iterrows():
    print(f"Cluster {int(row['cluster'])}")
    print(f" - Avg Location: ({row['lat']:.5f}, {row['lon']:.5f})")
    print(f" - Total Duration: {row['total_duration'] / 3600:.2f} hours")
    print(f" - Visits: {int(row['count'])}")
    print(f" - First Seen: {row['start_time']}")
    print(f" - Last Seen:  {row['end_time']}\n")

# ---- Step 6: Use Foursquare to Label Top 5 Locations ----
top5 = merged_stats.sort_values(by='total_duration', ascending=False).head(5)

def get_place_info(lat, lon):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "ll": f"{lat},{lon}",
        "radius": 100,
        "limit": 1,
        "sort": "DISTANCE"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if "results" in data and data["results"]:
            place = data["results"][0]
            name = place.get("name", "Unknown")
            categories = place.get("categories", [])
            category = categories[0]["name"] if categories else "Unknown"
            return name, category
        else:
            return "Unknown", "Unknown"
    except Exception as e:
        print(f"Error fetching Foursquare data: {e}")
        return "Error", "Error"

print("Top 5 Locations by Time Spent:\n")
for i, row in enumerate(top5.itertuples(), 1):
    lat = row.lat
    lon = row.lon
    if USE_FOURSQUARE:
        name, category = get_place_info(lat, lon)
    else:
        name, category = "N/A", "N/A"

    print(f"{i}. Cluster {int(row.cluster)}")
    print(f"   - Avg Location: ({lat:.5f}, {lon:.5f})")
    print(f"   - Time Spent: {row.total_duration / 3600:.2f} hours")
    print(f"   - Visits: {int(row.count)}")
    print(f"   - Place Name: {name}")
    print(f"   - Place Category: {category}\n")
