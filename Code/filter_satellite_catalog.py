import pandas as pd

# Load the CSV file
file_path = '../Data/space_track_satellites.csv'
df = pd.read_csv(file_path)

# Ensure the "DECAY" column is treated as datetime, treating invalid values as NaT
df['DECAY'] = pd.to_datetime(df['DECAY'], errors='coerce')

# Define the cutoff date
cutoff_date = pd.Timestamp('2020-09-01')

# Filter rows where "DECAY" is on or after the cutoff date OR is null/empty
filtered_df = df[(df['DECAY'].isna()) | (df['DECAY'] >= cutoff_date)]

# Save the filtered data back to a CSV file
filtered_df.to_csv('../Data/space_track_satellites_filtered.csv', index=False)

print("Rows with 'DECAY' before 2020-09-01 have been removed, null/empty values are retained.")