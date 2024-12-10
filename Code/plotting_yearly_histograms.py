import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# Load primary CDM dataset
csv_file = "../Data/output.csv"
data = pd.read_csv(csv_file)

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
bins = np.arange(data['SAT1_ALTITUDE_TCA'].min(), data['SAT1_ALTITUDE_TCA'].max() + bin_width, bin_width)

# Create colormap for coloring bars based on collision probability
colors = LinearSegmentedColormap.from_list("collision_prob", ["mistyrose", "darkred"], N=256)


# Function to calculate and plot histogram for a given year range
def plot_yearly_histogram(year_start, year_end):
    # Filter data by year range
    filtered_data = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)]

    # Combine SAT1 and SAT2 altitudes for the selected years
    filtered_altitudes = pd.concat([filtered_data['SAT1_ALTITUDE_TCA'], filtered_data['SAT2_ALTITUDE_TCA']]).dropna()
    print(filtered_altitudes)

    # Calculate histogram for the filtered altitudes (without normalization)
    yearly_counts, _ = np.histogram(filtered_altitudes, bins=bins)

    # Create the plot for this year range
    plt.figure(figsize=(10, 6))
    bars = plt.bar(bins[:-1], yearly_counts, width=np.diff(bins), color='blue', alpha=0.5, align='edge',
                   label=f'{year_start}-{year_end} Conjunctions')

    # Calculate average collision probability for each bin
    avg_collision_probs = []
    for i in range(len(bins) - 1):
        # Filter the data for SAT1 and SAT2 altitudes within the current bin
        sat1_bin_data = filtered_data[
            (filtered_data['SAT1_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT1_ALTITUDE_TCA'] < bins[i + 1])]
        sat2_bin_data = filtered_data[
            (filtered_data['SAT2_ALTITUDE_TCA'] >= bins[i]) & (filtered_data['SAT2_ALTITUDE_TCA'] < bins[i + 1])]
        bin_data = pd.concat([sat1_bin_data, sat2_bin_data], ignore_index=True)

        # Calculate average collision probability for this bin
        if bin_data.empty:
            avg_collision_prob = 0
        else:
            avg_collision_prob = bin_data['COLLISION_PROBABILITY'].mean()

        avg_collision_probs.append(avg_collision_prob)

    # Find the maximum average collision probability for scaling the colorbar
    max_avg_prob = float(np.quantile(avg_collision_probs, 0.99))

    # Apply colors to the bars based on the average collision probability
    for bar, avg_prob in zip(bars, avg_collision_probs):
        bar.set_facecolor(colors(avg_prob / max_avg_prob if max_avg_prob > 0 else 0))

    # Plot formatting
    plt.xlabel("Altitude (km)")
    plt.ylabel("Frequency of Conjunction Warnings (CDMs)")
    plt.title(f"CDM Warning Frequency at LEO Altitudes ({year_start}-{year_end})")
    sm = plt.cm.ScalarMappable(cmap=colors, norm=plt.Normalize(vmin=0, vmax=max_avg_prob))
    sm.set_array([])  # Required for colorbar
    plt.colorbar(sm, ax=plt.gca(), label="Average Collision Probability")
    bin_width_patch = mpatches.Patch(label='Bin Width: ' + str(bin_width) + ' km')
    plt.legend(handles=[bin_width_patch], handlelength=0, handletextpad=0)
    plt.xlim(200, 1800)
    plt.savefig(f'../Plots/CDM_histogram_{year_start}_{year_end}_{bin_width}_Bid_Width.png', dpi=300, bbox_inches='tight')
    plt.show()


# Plot histograms for 2021, 2022, and 2023 data
plot_yearly_histogram(2020, 2021)  # Includes 2020-2021 data
plot_yearly_histogram(2020, 2022)  # Includes 2020-2022 data
plot_yearly_histogram(2020, 2023)  # Includes 2020-2023 data
plot_yearly_histogram(2021, 2021)
plot_yearly_histogram(2022, 2023)