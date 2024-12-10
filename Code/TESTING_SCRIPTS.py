import pandas as pd
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm

# Load the New CDMs data
cdm_file = '../Data/NewCDMsSet.csv'
cdm_data = pd.read_csv(cdm_file)

# Initialize dictionaries for counts
country_counts = defaultdict(int)
operator_counts = defaultdict(int)
user_counts = defaultdict(int)

# Sets for unique countries, operators, and users
matched_countries = set()
matched_operators = set()
matched_users = set()

NORAD_ID_set = set()
NORAD_ID_list = []
with open('../Data/NewCDMsSet.csv', mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    # Iterate over each row in the CSV
    for row in reader:
        # Check if SAT1_OBJECT_TYPE or SAT2_OBJECT_TYPE is "PAYLOAD"
        if row['SAT1_OBJECT_TYPE'] == 'PAYLOAD':
            NORAD_ID_set.add(row['SAT1_OBJECT_DESIGNATOR'])
            NORAD_ID_list.append(row['SAT1_OBJECT_DESIGNATOR'])

        if row['SAT2_OBJECT_TYPE'] == 'PAYLOAD':
            NORAD_ID_set.add(row['SAT2_OBJECT_DESIGNATOR'])
            NORAD_ID_list.append(row['SAT2_OBJECT_DESIGNATOR'])

# Count occurrences of each NORAD ID in the list
norad_id_counts = Counter(NORAD_ID_list)

# Write the NORAD_ID and COUNT to a CSV file
output_file = '../Data/NORAD_ID_Counts.csv'

with open(output_file, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['NORAD_ID', 'COUNT'])  # Write header row

    # Write data rows for each NORAD ID in the set
    for norad_id in NORAD_ID_set:
        writer.writerow([norad_id, norad_id_counts[norad_id]])

print(f"CSV file with NORAD ID counts saved to {output_file}.")

# Load the UCS Satellite Database
ucs_file = '../Data/UCS-Satellite-Database 5-1-2023.xlsx'
ucs_data = pd.read_excel(ucs_file, sheet_name='Sheet1')
ucs_csv_file = '../Data/UCS_Satellite_Database.csv'
norad_data = pd.read_csv(output_file)

# Initialize sets and counters
matched_countries = set()
matched_operators = set()
matched_users = set()

country_counts = defaultdict(int)
operator_counts = defaultdict(int)
user_counts = defaultdict(int)

# Explicit loop through NORAD_ID_Counts
for _, norad_row in norad_data.iterrows():
    norad_id = int(norad_row['NORAD_ID'])  # Convert NORAD_ID to integer
    appearances = int(norad_row['COUNT'])  # Get the number of appearances

    # Loop through UCS data to find matches
    for _, ucs_row in ucs_data.iterrows():
        ucs_norad_id = int(ucs_row['NORAD Number'])  # Convert NORAD Number to integer

        # Check if NORAD IDs match
        if norad_id == ucs_norad_id:
            # Extract and clean data
            country = ucs_row['Country of Operator/Owner'].strip().upper()
            operator = ucs_row['Operator/Owner'].strip().upper()
            users = ucs_row['Users'].split('/') if pd.notnull(ucs_row['Users']) else []

            # Update sets
            matched_countries.add(country)
            matched_operators.add(operator)
            for user in users:
                matched_users.add(user.strip().upper())

            # Update counts using the number of appearances
            country_counts[country] += appearances
            operator_counts[operator] += appearances
            for user in users:
                user_counts[user.strip().upper()] += appearances

# Output results
print("Matched Countries:", matched_countries)
print("Matched Operators:", matched_operators)
print("Matched Users:", matched_users)
print("Country Counts:", dict(country_counts))
print("Operator Counts:", dict(operator_counts))
print("User Counts:", dict(user_counts))

# Save results to CSV files
country_output_file = '../Data/Country_Counts.csv'
operator_output_file = '../Data/Operator_Counts.csv'
user_output_file = '../Data/User_Counts.csv'

# Save country counts
pd.DataFrame(country_counts.items(), columns=['Country', 'Count']).to_csv(country_output_file, index=False)

# Save operator counts
pd.DataFrame(operator_counts.items(), columns=['Operator', 'Count']).to_csv(operator_output_file, index=False)

# Save user counts
pd.DataFrame(user_counts.items(), columns=['User', 'Count']).to_csv(user_output_file, index=False)

print(f"Country counts saved to {country_output_file}")
print(f"Operator counts saved to {operator_output_file}")
print(f"User counts saved to {user_output_file}")
# # Visualization function
# def plot_bar_chart(data_dict, title, xlabel, ylabel, filename):
#     # Sort dictionary by values in descending order
#     sorted_data = dict(sorted(data_dict.items(), key=lambda x: x[1], reverse=True))
#     keys = list(sorted_data.keys())
#     values = list(sorted_data.values())
#
#     plt.figure(figsize=(10, 6))
#     plt.bar(keys, values, color='skyblue')
#     plt.title(title)
#     plt.xlabel(xlabel)
#     plt.ylabel(ylabel)
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()
#     plt.savefig(f'../Plots/{filename}.png', dpi=300)
#     plt.show()
#
#
# # Plot total counts
# plot_bar_chart(country_counts, 'Total CDMs by Country', 'Country', 'CDM Count', 'TotalCDMsByCountry')
# plot_bar_chart(operator_counts, 'Total CDMs by Operator/Owner', 'Operator/Owner', 'CDM Count', 'TotalCDMsByOperator')
# plot_bar_chart(user_counts, 'Total CDMs by Users', 'Users', 'CDM Count', 'TotalCDMsByUsers')