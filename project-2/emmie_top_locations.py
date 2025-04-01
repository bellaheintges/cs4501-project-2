import matplotlib.pyplot as plt

# Define custom labels using cluster info
custom_labels = [
    "Home (Charlottesville)",
    "Unknown (DR)",
    "Home (New Orleans)",
    "Kardinal Hall",
    "Home (Bethesda)"
]

# Match durations (in hours) to each cluster
durations_hours = [721, 78.34, 22.57, 15.02, 13.59]

plt.figure(figsize=(10, 6))
plt.bar(custom_labels, durations_hours)
plt.xlabel('Place')
plt.ylabel('Time Spent (Hours)')
plt.title('Top 5 Locations by Time Spent')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
