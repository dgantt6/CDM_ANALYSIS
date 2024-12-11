import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

# Load primary CDM dataset
cdm_file = "../Data/output.csv"
data = pd.read_csv(cdm_file)

# Load satellite dataset
satellite_file = "../Data/space_track_satellites_filtered.csv"
satellite_data = pd.read_csv(satellite_file)
satellite_data['ALTITUDE'] = pd.to_numeric(satellite_data['ALTITUDE'], errors='coerce')

# Convert SAT1_ALTITUDE_TCA and SAT2_ALTITUDE_TCA to numeric and kilometers
data['SAT1_ALTITUDE_TCA'] = pd.to_numeric(data['SAT1_ALTITUDE_TCA'], errors='coerce') / 1000  # Convert to km
data['SAT2_ALTITUDE_TCA'] = pd.to_numeric(data['SAT2_ALTITUDE_TCA'], errors='coerce') / 1000  # Convert to km

# Convert COLLISION_PROBABILITY to numeric
data['COLLISION_PROBABILITY'] = pd.to_numeric(data['COLLISION_PROBABILITY'], errors='coerce')

# Convert TCA column to datetime and extract year
data['TCA'] = pd.to_datetime(data['TCA'], errors='coerce')
data['Year'] = data['TCA'].dt.year

# Define histogram parameters
bin_width = 10  # Width of each altitude bin in km
bins = np.arange(data[['SAT1_ALTITUDE_TCA', 'SAT2_ALTITUDE_TCA']].min().min(),
                 data[['SAT1_ALTITUDE_TCA', 'SAT2_ALTITUDE_TCA']].max().max() + bin_width, bin_width)

# Define colormap for collision probability and miss distance
collision_colors = LinearSegmentedColormap.from_list("collision_prob", ["mistyrose", "darkred"], N=256)
miss_distance_colors = LinearSegmentedColormap.from_list("miss_distance", ["mistyrose", "darkred"], N=256)

# Function to overlay satellite data
def overlay_satellite_data(ax):
    payload_altitudes = satellite_data[satellite_data['OBJECT_TYPE'] == 'PAYLOAD']['ALTITUDE']
    print(len(payload_altitudes))
    debris_altitudes = satellite_data[satellite_data['OBJECT_TYPE'].isin(['DEBRIS', 'ROCKET BODY'])]['ALTITUDE']
    print(len(debris_altitudes))
    payload_counts, _ = np.histogram(payload_altitudes, bins=bins)
    debris_counts, _ = np.histogram(debris_altitudes, bins=bins)

    # Add a secondary y-axis for satellite counts
    satellite_ax = ax.twinx()
    # Axis title for Number of Space Objects (right axis)
    satellite_ax.set_ylabel("Number of Space Objects", labelpad=12, fontsize=12)
    right_patch_blue = mpatches.Rectangle((1.06, 0.2), 0.019, 0.05, transform=ax.transAxes, color='blue',
                                    clip_on=False)
    ax.add_patch(right_patch_blue)
    right_patch_green = mpatches.Rectangle((1.06, 0.14), 0.019, 0.05, transform=ax.transAxes, color='green',
                                    clip_on=False)
    ax.add_patch(right_patch_green)

    # Plot lines for satellites
    satellite_ax.step(bins[:-1], payload_counts, where='mid', label='Satellites', color='blue', linewidth=2)
    satellite_ax.step(bins[:-1], debris_counts, where='mid', label='Debris', color='green', linewidth=2)
    satellite_ax.set_ylim(bottom=0)

    # Add legends
    ax.legend(loc='upper left')
    satellite_ax.legend(loc='upper right')

# Function to plot yearly histograms for collision probability
def plot_yearly_collision_probability(year):
    filtered_data = data[data['Year'] == year]
    combined_altitudes = pd.concat([filtered_data['SAT1_ALTITUDE_TCA'], filtered_data['SAT2_ALTITUDE_TCA']]).dropna()
    yearly_counts, _ = np.histogram(combined_altitudes, bins=bins)

    avg_collision_probs = []
    for i in range(len(bins) - 1):
        bin_data = filtered_data[(filtered_data['SAT1_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT1_ALTITUDE_TCA'] < bins[i + 1]) |
                                  (filtered_data['SAT2_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT2_ALTITUDE_TCA'] < bins[i + 1])]
        avg_collision_probs.append(bin_data['COLLISION_PROBABILITY'].mean() if not bin_data.empty else 0)

    max_avg_prob = float(np.nanquantile(avg_collision_probs, 0.90))

    plt.figure(figsize=(12, 8))
    bars = plt.bar(bins[:-1], yearly_counts, width=np.diff(bins), color='blue', alpha=0.5, align='edge')
    for bar, avg_prob in zip(bars, avg_collision_probs):
        bar.set_facecolor(collision_colors(avg_prob / max_avg_prob if max_avg_prob > 0 else 0))

    plt.xlabel("Altitude (km)")
    plt.ylabel('Number of CDMs')
    sm = plt.cm.ScalarMappable(cmap=collision_colors, norm=plt.Normalize(vmin=0, vmax=max_avg_prob))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca(), label="Average Collision Probability in Altitude Shell", orientation='horizontal', pad=0.12, aspect = 50)
    cbar.ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    cbar.ax.xaxis.get_major_formatter().set_scientific(True)
    cbar.ax.xaxis.get_major_formatter().set_powerlimits((-1, 1))
    plt.xlim(200, 1800)
    plt.savefig(f'../Plots/CDM_collision_probability_{year}.png', dpi=300, bbox_inches='tight')
    plt.show()

# Function to plot study period for collision probability
def plot_study_period_collision_probability():
    combined_altitudes = pd.concat([data['SAT1_ALTITUDE_TCA'], data['SAT2_ALTITUDE_TCA']]).dropna()
    total_counts, _ = np.histogram(combined_altitudes, bins=bins)

    avg_collision_probs = []
    for i in range(len(bins) - 1):
        bin_data = data[(data['SAT1_ALTITUDE_TCA'] >= bins[i]) & (data['SAT1_ALTITUDE_TCA'] < bins[i + 1]) |
                        (data['SAT2_ALTITUDE_TCA'] >= bins[i]) & (data['SAT2_ALTITUDE_TCA'] < bins[i + 1])]
        avg_collision_probs.append(bin_data['COLLISION_PROBABILITY'].mean() if not bin_data.empty else 0)

    max_avg_prob = float(np.nanquantile(avg_collision_probs, 0.90))

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(bins[:-1], total_counts, width=np.diff(bins), color='blue', alpha=0.5, align='edge')
    for bar, avg_prob in zip(bars, avg_collision_probs):
        bar.set_facecolor(collision_colors(avg_prob / max_avg_prob if max_avg_prob > 0 else 0))

    ax.set_xlabel("Altitude (km)")
    # Axis title for Number of CDMs (left axis)
    midpoint_color = mcolors.to_rgba("mistyrose", alpha=0.5)[:3]  # Blend mistyrose and darkred
    midpoint_color = tuple((a + b) / 2 for a, b in zip(midpoint_color, mcolors.to_rgba("darkred")[:3]))
    plt.ylabel("Number of CDMs", labelpad=10, fontsize=12)
    left_patch = mpatches.Rectangle((-0.075, 0.28), 0.019, 0.05, transform=ax.transAxes, color=midpoint_color,
                                    clip_on=False)
    ax.add_patch(left_patch)
    sm = plt.cm.ScalarMappable(cmap=collision_colors, norm=plt.Normalize(vmin=0, vmax=max_avg_prob))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca(), label="Average Collision Probability in Altitude Shell", orientation='horizontal', pad=0.12, aspect=50)
    cbar.ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    cbar.ax.xaxis.get_major_formatter().set_scientific(True)
    cbar.ax.xaxis.get_major_formatter().set_powerlimits((-1, 1))
    overlay_satellite_data(ax)
    ax.set_xlim(200, 1800)
    plt.savefig(f'../Plots/CDM_study_period_collision_probability.png', dpi=300, bbox_inches='tight')
    plt.show()

# Generate plots
for year in [2021, 2022, 2023]:
    plot_yearly_collision_probability(year)
plot_study_period_collision_probability()