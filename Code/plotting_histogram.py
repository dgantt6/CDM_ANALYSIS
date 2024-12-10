import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# Load CSV
csv_file = "../Data/output.csv"
data = pd.read_csv(csv_file)

# Convert SAT1_ALTITUDE_TCA and SAT2_ALTITUDE_TCA to numeric and to kilometers
data['SAT1_ALTITUDE_TCA'] = pd.to_numeric(data['SAT1_ALTITUDE_TCA'], errors='coerce') / 1000  # Convert to km
data['SAT2_ALTITUDE_TCA'] = pd.to_numeric(data['SAT2_ALTITUDE_TCA'], errors='coerce') / 1000  # Convert to km

# Convert COLLISION_PROBABILITY to numeric
data['COLLISION_PROBABILITY'] = pd.to_numeric(data['COLLISION_PROBABILITY'], errors='coerce')

# Combine altitudes for histogram
combined_altitudes = pd.concat([data['SAT1_ALTITUDE_TCA'], data['SAT2_ALTITUDE_TCA']])
combined_altitudes = combined_altitudes.dropna()

# Set number of bins
bin_width = 10 # Increase bin width to reduce empty bins
bin_count = int((combined_altitudes.max() - combined_altitudes.min()) / bin_width)

# Define the study period
start_year = 2020
end_year = 2024
study_months = (2024 - 2020 - 1) * 12 + 8
study_years = study_months / 12

# Create histogram data
plt.figure(figsize=(10, 6))
counts, bins = np.histogram(combined_altitudes, bins=bin_count)
normalized_counts = counts / study_years
bars = plt.bar(bins[:-1], normalized_counts, width=np.diff(bins), color='blue', alpha=0.5, align='edge', label='Average CDMs per Year')


# Calculate average collision probability for each bin
avg_collision_probs = []
for i in range(len(bins) - 1):
    # Filter data for SAT1 and SAT2 altitudes within the current bin
    sat1_bin_data = data[(data['SAT1_ALTITUDE_TCA'] >= bins[i]) & (data['SAT1_ALTITUDE_TCA'] < bins[i + 1])]
    sat2_bin_data = data[(data['SAT2_ALTITUDE_TCA'] >= bins[i]) & (data['SAT2_ALTITUDE_TCA'] < bins[i + 1])]
    bin_data = pd.concat([sat1_bin_data, sat2_bin_data], ignore_index=True)

    # Handle empty bins
    if bin_data.empty:
        avg_collision_prob = 0  # Assign zero if no data in the bin
    else:
        avg_collision_prob = bin_data['COLLISION_PROBABILITY'].mean()

    avg_collision_probs.append(avg_collision_prob)

# Find the maximum average collision probability for scaling the colorbar
max_avg_prob = np.quantile(avg_collision_probs, 0.99)

# Create colormap and apply colors to bars
colors = LinearSegmentedColormap.from_list("collision_prob", ["mistyrose", "darkred"], N=256)
for bar, avg_prob in zip(bars, avg_collision_probs):
    bar.set_facecolor(colors(avg_prob / max_avg_prob if max_avg_prob > 0 else 0))

# Plot Formatting
plt.xlabel("Altitude (km)")
plt.ylabel("Frequency of Payload Conjunction Warning (CDMs/year)")
plt.title("CDM Warning Frequency at LEO Altitudes (Entire Study Period)")
sm = plt.cm.ScalarMappable(cmap=colors, norm=plt.Normalize(vmin=0, vmax=max_avg_prob))
sm.set_array([])  # Required for colorbar
plt.xlim(200, 1800)
plt.colorbar(sm, ax=plt.gca(), label="Average Collision Probability")
bin_width_patch = mpatches.Patch(label='Bin Width: ' + str(bin_width) + ' km')
plt.legend(handles=[bin_width_patch], handlelength=0, handletextpad=0)
plt.savefig('../Plots/CDM_histogram_{bin_width}_Bid_Width.png', dpi=300, bbox_inches='tight')
plt.show()# Create a Patch object for the bin width

# Additional calculations for frequency of CDMs by miss distance
def plot_miss_distance_histograms():
    miss_distance_bins = {
        '0-100 m': (0, 100),
        '100-200 m': (100, 200),
        '>300 m': (300, float('inf'))
    }

    for label, (lower, upper) in miss_distance_bins.items():
        # Filter CDMs by miss distance
        filtered_data = data[(data['MISS_DISTANCE'] >= lower) & (data['MISS_DISTANCE'] < upper)]

        # Combine SAT1 and SAT2 altitudes
        filtered_altitudes = pd.concat([filtered_data['SAT1_ALTITUDE_TCA'], filtered_data['SAT2_ALTITUDE_TCA']]).dropna()

        # Calculate histogram
        yearly_counts, _ = np.histogram(filtered_altitudes, bins=bins)

        # Plot the histogram
        plt.figure(figsize=(10, 6))
        plt.bar(bins[:-1], yearly_counts, width=np.diff(bins), color='green', alpha=0.6, align='edge', label=label)
        plt.xlabel("Altitude (km)")
        plt.ylabel("Frequency of Conjunction Warnings (CDMs)")
        plt.title(f"CDM Warning Frequency by Miss Distance ({label})")
        plt.legend()
        plt.xlim(200, 1800)
        plt.savefig(f'../Plots/CDM_histogram_miss_distance_{label}_{bin_width}_Bid_Width.png', dpi=300, bbox_inches='tight')
        plt.show()

# Ensure 'Year' column is created
if 'TCA' in data.columns:
    data['TCA'] = pd.to_datetime(data['TCA'], errors='coerce')
    data['Year'] = data['TCA'].dt.year
else:
    print("Error: 'TCA' column not found. Ensure the dataset has a valid 'TCA' column.")

# Function to plot histograms by miss distance with updated labels
def plot_miss_distance_histograms():
    miss_distance_bins = {
        '0-100 m': (0, 100),
        '100-300 m': (100, 300),
        '>300 m': (300, float('inf'))
    }

    for label, (lower, upper) in miss_distance_bins.items():
        filtered_data = data[(data['MISS_DISTANCE'] >= lower) & (data['MISS_DISTANCE'] < upper)]
        filtered_altitudes = pd.concat([filtered_data['SAT1_ALTITUDE_TCA'], filtered_data['SAT2_ALTITUDE_TCA']]).dropna()

        yearly_counts, _ = np.histogram(filtered_altitudes, bins=bins)

        plt.figure(figsize=(10, 6))
        plt.bar(bins[:-1], yearly_counts, width=np.diff(bins), color='green', alpha=0.6, align='edge', label=f"{label}, Bin Width: {bin_width} km")
        plt.xlabel("Altitude (km)")
        plt.ylabel("Frequency of Conjunction Warnings (CDMs)")
        plt.title(f"CDM Warning Frequency by Miss Distance ({label})")
        plt.legend()
        plt.xlim(200, 1800)
        plt.savefig(f'../Plots/CDM_histogram_miss_distance_{label.replace(" ", "_")}_{bin_width}_Bid_Width.png', dpi=300, bbox_inches='tight')
        plt.show()

# Updated yearly histogram function with miss distance coloring and labels
def plot_yearly_histogram_with_miss_distance(year_start, year_end):
    if 'Year' not in data.columns:
        print("Error: 'Year' column not found. Ensure the dataset has a valid 'Year' column.")
        return

    filtered_data = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)]
    filtered_altitudes = pd.concat([filtered_data['SAT1_ALTITUDE_TCA'], filtered_data['SAT2_ALTITUDE_TCA']]).dropna()
    yearly_counts, _ = np.histogram(filtered_altitudes, bins=bins)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(bins[:-1], yearly_counts, width=np.diff(bins), color='blue', alpha=0.5, align='edge')

    avg_miss_distances = []
    for i in range(len(bins) - 1):
        sat1_bin_data = filtered_data[
            (filtered_data['SAT1_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT1_ALTITUDE_TCA'] < bins[i + 1])]
        sat2_bin_data = filtered_data[
            (filtered_data['SAT2_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT2_ALTITUDE_TCA'] < bins[i + 1])]
        bin_data = pd.concat([sat1_bin_data, sat2_bin_data], ignore_index=True)

        avg_miss_distance = bin_data['MISS_DISTANCE'].mean() if not bin_data.empty else 0
        avg_miss_distances.append(avg_miss_distance)

    max_avg_miss_distance = float(np.nanquantile(avg_miss_distances, 0.99))

    for bar, avg_distance in zip(bars, avg_miss_distances):
        bar.set_facecolor(colors(avg_distance / max_avg_miss_distance if max_avg_miss_distance > 0 else 0))

    plt.xlabel("Altitude (km)")
    plt.ylabel("Frequency of Conjunction Warnings (CDMs)")
    plt.title(f"CDM Warning Frequency with Miss Distance ({year_start}-{year_end})")
    sm = plt.cm.ScalarMappable(cmap=colors, norm=plt.Normalize(vmin=0, vmax=max_avg_miss_distance))
    sm.set_array([])
    plt.colorbar(sm, ax=plt.gca(), label="Average Miss Distance (m)")
    bin_width_ = mpatches.Patch(label='Bin Width: ' + str(bin_width) + ' km')
    plt.legend(handles=[bin_width_], handlelength=0, handletextpad=0)
    plt.xlim(200, 1800)
    plt.savefig(f'../Plots/CDM_histogram_{year_start}_{year_end}_miss_distance_{bin_width}_Bid_Width.png', dpi=300, bbox_inches='tight')
    plt.show()

# Plot updated histograms
plot_miss_distance_histograms()
plot_yearly_histogram_with_miss_distance(2020, 2021)
plot_yearly_histogram_with_miss_distance(2020, 2022)
plot_yearly_histogram_with_miss_distance(2020, 2023)
plot_yearly_histogram_with_miss_distance(2021, 2021)
plot_yearly_histogram_with_miss_distance(2022, 2023)
