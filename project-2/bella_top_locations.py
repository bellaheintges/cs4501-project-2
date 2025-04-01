import matplotlib.pyplot as plt

# Define custom labels using cluster info
custom_labels = [
    "Home (Charlottesville)",
    "Home (Dallas)",
    "Unknown (DR)",
    "Kardinal Hall",
    "North Grounds (Charlottesville)"
]

# Match durations (in hours) to each cluster
durations_hours = [762.5, 108.0, 42.83, 10.78, 10.58]

plt.figure(figsize=(10, 6))
plt.bar(custom_labels, durations_hours)
plt.xlabel('Place')
plt.ylabel('Time Spent (Hours)')
plt.title('Top 5 Locations by Time Spent')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
