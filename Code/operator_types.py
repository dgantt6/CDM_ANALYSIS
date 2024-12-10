import csv
import re
from collections import defaultdict
import pandas as pd

# Grab the satellite information from UCS Databsae
keywords = []
with open('../Data/UCS-Satellite-Database 5-1-2023.xlsx', 'r') as f:
    xl = pd.ExcelFile(f)
    df = xl.parse('Sheet1')
    keywords = [row[0] for row in reader]


with open('../Data/unmatched_rows.csv', mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        satellite_name = row['SAT_OBJECT_NAME']
        if '/' in satellite_name:
            split_names = satellite_name.split('/')
            for name in split_names:
                cleaned_name = re.sub(r'\s*\d+\s*$', '', name)
                keywords.append(cleaned_name.strip())

        elif re.search(r'\d-\s*$', satellite_name):
            cleaned_name = re.sub(r'\d-\s*$', '', satellite_name).strip()
            keywords.append(cleaned_name)

        elif re.search(r'\s*\d+[A-Za-z]-*\d*[A-Za-z]*\s*$', satellite_name):
            cleaned_name = re.sub(r'\s*\d+[A-Za-z]-*\d*[A-Za-z]*\s*$', '', satellite_name).strip()
            keywords.append(cleaned_name)

        elif '(' in satellite_name:
            split_names = re.split(r'\(|\)', satellite_name)
            for name in split_names:
                if name != '':
                    cleaned_name = re.sub(r'\s*\d+\s*$', '', name)
                    keywords.append(cleaned_name.strip())

        # Default case
        else:
            cleaned_name = re.sub(r'\s*\d+\s*$', '', satellite_name)
            keywords.append(cleaned_name.strip())


# Create a dictionary to count the occurrences of each keyword
keyword_counts = defaultdict(int)

# Set to store rows with unmatched payload types
unmatched_rows = set()

# Open your CSV file for reading
with open('../Data/NewCDMsSet.csv', mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    # Iterate over each row in the CSV
    for row in reader:
        # Check if SAT1_OBJECT_TYPE or SAT2_OBJECT_TYPE is "PAYLOAD"
        if row['SAT1_OBJECT_TYPE'] == 'PAYLOAD':
            for keyword in keywords:
                if keyword in row['SAT1_OBJECT_NAME']:
                    keyword_counts[keyword] += 1

        if row['SAT2_OBJECT_TYPE'] == 'PAYLOAD':
            for keyword in keywords:
                if keyword in row['SAT2_OBJECT_NAME']:
                    keyword_counts[keyword] += 1

        # If no keyword is matched for this row, save it in unmatched_rows
        if row['SAT1_OBJECT_TYPE'] == 'PAYLOAD' and not any(keyword in row['SAT1_OBJECT_NAME'] for keyword in keywords):
            unmatched_rows.add(row['SAT1_OBJECT_NAME'])
        if row['SAT2_OBJECT_TYPE'] == 'PAYLOAD' and not any(keyword in row['SAT2_OBJECT_NAME'] for keyword in keywords):
            unmatched_rows.add(row['SAT2_OBJECT_NAME'])
# Output the counts for each keyword
print("Keyword counts:")

with open('../Data/keywords.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['KEYWORD','COUNT'])
    for keyword, count in keyword_counts.items():
        print(f"{keyword}: {count}")
        writer.writerow([keyword, count])

# Save unmatched rows to a file (only saving the object names)
with open('../Data/unmatched_rows.csv', mode='w', newline='') as unmatched_file:
    writer = csv.writer(unmatched_file)
    writer.writerow(['SAT_OBJECT_NAME'])  # Write header for object names
    # Iterate through unmatched rows
    for row in unmatched_rows:
        # Write the object names only
        writer.writerow([row])

with open('../Data/high_count_keywords.csv', 'w', newline='') as high_count_file:
    writer = csv.writer(high_count_file)
    writer.writerow(['KEYWORD', 'COUNT'])
    for keyword, count in keyword_counts.items():
        if count > 100:
            writer.writerow([keyword, count])

print(f"Unmatched rows have been saved to 'unmatched_rows.csv'.")
print(f"The number of keywords is {len(keywords)}.")

