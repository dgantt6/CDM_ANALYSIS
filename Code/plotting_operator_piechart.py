import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

plt.close('all')

# Load datasets
cdm_file = "../Data/output.csv"
satellite_file = "../Data/space_track_satellites_filtered.csv"
countries_file = "../Data/space_track_countries.csv"

# Load data
cdm_data = pd.read_csv(cdm_file)
satellite_data = pd.read_csv(satellite_file)
countries_data = pd.read_csv(countries_file)

# Ensure data consistency
countries_data.columns = ['COUNTRY_ABBR', 'COUNTRY_FULL']

# Combine SAT1 and SAT2 object types, ensuring no duplicates
sat1_types = cdm_data['SAT1_OBJECT_DESIGNATOR'].dropna().unique()
sat2_types = cdm_data['SAT2_OBJECT_DESIGNATOR'].dropna().unique()
all_types = pd.Series(list(set(sat1_types).union(set(sat2_types))))

# Filter for PAYLOAD satellites
payload_types = all_types[all_types.isin(satellite_data[satellite_data['OBJECT_TYPE'] == 'PAYLOAD']['NORAD_CAT_ID'])]

# Count occurrences of PAYLOAD satellites in CDM data
payload_cdm_counts = cdm_data[(cdm_data['SAT1_OBJECT_DESIGNATOR'].isin(payload_types)) |
                              (cdm_data['SAT2_OBJECT_DESIGNATOR'].isin(payload_types))]
counts_by_payload = payload_cdm_counts[['SAT1_OBJECT_DESIGNATOR', 'SAT2_OBJECT_DESIGNATOR']].stack().value_counts()
counts_by_payload = counts_by_payload[counts_by_payload.index.isin(payload_types)].reset_index()
counts_by_payload.columns = ['NORAD_CAT_ID', 'COUNT']

# Map satellite IDs to countries
satellite_data_filtered = satellite_data[satellite_data['OBJECT_TYPE'] == 'PAYLOAD']
merged_data = pd.merge(counts_by_payload, satellite_data_filtered, left_on='NORAD_CAT_ID', right_on='NORAD_CAT_ID', how='inner')

# Map country abbreviations to full names
merged_data = pd.merge(merged_data, countries_data, left_on='COUNTRY', right_on='COUNTRY_ABBR', how='inner')

# Group by country and sum counts for CDMs
country_counts_cdm = merged_data.groupby('COUNTRY_FULL')['COUNT'].sum().reset_index()
total_cdm_counts = country_counts_cdm['COUNT'].sum()
country_counts_cdm['PERCENTAGE'] = (country_counts_cdm['COUNT'] / total_cdm_counts) * 100

# Process satellite dataset for PAYLOAD satellites
satellite_counts = satellite_data_filtered['COUNTRY'].value_counts().reset_index()
satellite_counts.columns = ['COUNTRY_ABBR', 'COUNT']
satellite_counts = pd.merge(satellite_counts, countries_data, left_on='COUNTRY_ABBR', right_on='COUNTRY_ABBR', how='inner')
total_satellite_counts = satellite_counts['COUNT'].sum()
satellite_counts['PERCENTAGE'] = (satellite_counts['COUNT'] / total_satellite_counts) * 100

# Ensure "Other" consistency with 1% rule
def group_countries_by_percentage(df, threshold, total_column='COUNT', percentage_column='PERCENTAGE'):
    other_count = df[df[percentage_column] < threshold][total_column].sum()
    grouped = df[df[percentage_column] >= threshold].copy()
    if other_count > 0:
        grouped = pd.concat([grouped, pd.DataFrame({'COUNTRY_FULL': ['Other'], total_column: [other_count]})])
    return grouped

country_counts_cdm_grouped = group_countries_by_percentage(country_counts_cdm, 1)
satellite_counts_grouped = group_countries_by_percentage(satellite_counts, 1)

# Create a consistent color mapping
unique_countries = set(country_counts_cdm_grouped['COUNTRY_FULL']).union(set(satellite_counts_grouped['COUNTRY_FULL']))
colors = list(mcolors.TABLEAU_COLORS.values())
color_mapping = {country: colors[i % len(colors)] for i, country in enumerate(unique_countries)}

# Add "Other" to color mapping if not already present
if 'Other' not in color_mapping:
    color_mapping['Other'] = 'gray'

# Pie chart figure
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

# CDM Pie Chart
axes[0].pie(
    country_counts_cdm_grouped['COUNT'],
    labels=country_counts_cdm_grouped['COUNTRY_FULL'],
    labeldistance=1.2,
    autopct='%1.1f%%',
    startangle=140,
    colors=[color_mapping[country] for country in country_counts_cdm_grouped['COUNTRY_FULL']],
    pctdistance=1.1  # Adjust the distance of percentages from the center
)
axes[0].set_title("Unique CDMs by Operator \n (Sept. 2020 - Apr. 2024)")

# Satellite Pie Chart
axes[1].pie(
    satellite_counts_grouped['COUNT'],
    labels=satellite_counts_grouped['COUNTRY_FULL'],
    labeldistance = 1.2,
    autopct='%1.1f%%',
    startangle=140,
    colors=[color_mapping[country] for country in satellite_counts_grouped['COUNTRY_FULL']],
    pctdistance= 1.1  # Adjust the distance of percentages from the center
)
axes[1].set_title("Total Satellites in LEO by Operator \n (Apr 2024)")

# Save and show
plt.tight_layout()
plt.savefig("../Plots/combined_pie_chart.png")
plt.show()

# Export "Other" countries
pd.DataFrame({'CDM_Other': country_counts_cdm[country_counts_cdm['PERCENTAGE'] < 1]['COUNTRY_FULL']}).to_csv("../Data/cdm_other_countries.csv", index=False)
pd.DataFrame({'Satellite_Other': satellite_counts[satellite_counts['PERCENTAGE'] < 1]['COUNTRY_FULL']}).to_csv("../Data/satellite_other_countries.csv", index=False)

