import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# List of colors
color_palette = [
    '#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B',
    '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF', '#9EDAE5', '#C49C94',
    '#F7B6D2', '#C7C7C7', '#DBDB8D', '#9EDAE5'
]
color_index = 0
# Define the study period
start_year = 2020
end_year = 2024
study_months = (2024 - 2020 - 1) * 12 + 8
study_years = study_months / 12
print(study_years)

def generate_color():
    global color_index
    color = color_palette[color_index]
    color_index = (color_index + 1) % len(color_palette)
    return color


# Initialize dictionaries to store aggregated data
country_counts = defaultdict(int)  # For "COUNT" by country
country_counts_per_week = defaultdict(float)  # For "COUNT_PER_WEEK" by country
operator_type_counts = defaultdict(int)  # For "COUNT" by operator type
operator_type_counts_per_week = defaultdict(float)  # For "COUNT_PER_WEEK" by operator type

# Open and process the CSV file
with open('../Data/high_count_operators.csv', mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        # Handle the "COUNTRY" column (splitting by '/')
        countries = row['COUNTRY'].split('/')  # Split countries by '/'
        count = int(float(row['COUNT_PER_YEAR']))  # Convert "COUNT" to integer
        count_per_week = float(row['COUNT_PER_WEEK'])  # Convert "COUNT_PER_WEEK" to float

        for country in countries:
            country = country.strip()  # Remove any leading/trailing spaces
            country_counts[country] += count
            country_counts_per_week[country] += count_per_week

        # Handle the "OPERATOR_TYPE" column
        operator_type = row['OPERATOR_TYPE'].strip()  # Remove any leading/trailing spaces
        operator_type_counts[operator_type] += count
        operator_type_counts_per_week[operator_type] += count_per_week

# Sort dictionaries
country_counts = dict(sorted(country_counts.items(), key=lambda item: item[1], reverse=True))
country_counts_per_week = dict(sorted(country_counts_per_week.items(), key=lambda item: item[1], reverse=True))
operator_type_counts = dict(sorted(operator_type_counts.items(), key=lambda item: item[1], reverse=True))
operator_type_counts_per_week = dict(sorted(operator_type_counts_per_week.items(), key=lambda item: item[1], reverse=True))

# Plotting the results
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Aggregated Satellite Data', fontsize=16)

# Bar plot for "COUNT" by country
axes[0, 0].bar(country_counts.keys(), country_counts.values(), color='skyblue')
axes[0, 0].set_title('Total CDMs by Country')
axes[0, 0].set_xlabel('Country')
axes[0, 0].set_ylabel('CDMs Per Year')
axes[0, 0].tick_params(axis='x', rotation=45)

# Bar plot for "COUNT_PER_WEEK" by country
axes[0, 1].bar(country_counts_per_week.keys(), country_counts_per_week.values(), color='orange')
axes[0, 1].set_title('CDMs Per Week by Country')
axes[0, 1].set_xlabel('Country')
axes[0, 1].set_ylabel('CDM Count Per Week')
axes[0, 1].tick_params(axis='x', rotation=45)

# Bar plot for "COUNT" by operator type
axes[1, 0].bar(operator_type_counts.keys(), operator_type_counts.values(), color='green')
axes[1, 0].set_title('Total CDMs by Operator Type')
axes[1, 0].set_xlabel('Operator Type')
axes[1, 0].set_ylabel('CDMs Per Year')
axes[1, 0].tick_params(axis='x', rotation=45)

# Bar plot for "COUNT_PER_WEEK" by operator type
axes[1, 1].bar(operator_type_counts_per_week.keys(), operator_type_counts_per_week.values(), color='red')
axes[1, 1].set_title('CDMs Per Week by Operator Type')
axes[1, 1].set_xlabel('Operator Type')
axes[1, 1].set_ylabel('CDMs Per Week')
axes[1, 1].tick_params(axis='x', rotation=45)

# Adjust layout and show the plots
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('../Plots/AggregatedOperatorData.png', dpi=300, bbox_inches='tight')
plt.show()



# Dictionaries to store consistent colors
country_colors = {}
operator_type_colors = {}

# Assign colors to countries
for country in country_counts:
    country_colors[country] = generate_color()

# Assign colors to operator types
for operator in operator_type_counts:
    operator_type_colors[operator] = generate_color()

# Individual plot for "Total CDMs by Country"
plt.figure(figsize=(8, 6))
colors = [country_colors[country] for country in country_counts.keys()]
plt.bar(country_counts.keys(), country_counts.values(), color=colors)
plt.title('Total CDMs by Country')
plt.xlabel('Country')
plt.ylabel('CDMs Per Year')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../Plots/TotalCDMsByCountry.png', dpi=300, bbox_inches='tight')

# Individual plot for "CDMs Per Week by Country"
plt.figure(figsize=(8, 6))
colors = [country_colors[country] for country in country_counts_per_week.keys()]
plt.bar(country_counts_per_week.keys(), country_counts_per_week.values(), color=colors)
plt.title('CDMs Per Week by Country')
plt.xlabel('Country')
plt.ylabel('CDM Count Per Week')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../Plots/TotalCDMsPerWeekByCountry.png', dpi=300, bbox_inches='tight')
plt.show()

# Individual plot for "Total CDMs by Operator Type"
plt.figure(figsize=(8, 6))
colors = [operator_type_colors[operator] for operator in operator_type_counts.keys()]
plt.bar(operator_type_counts.keys(), operator_type_counts.values(), color=colors)
plt.title('Total CDMs by Operator Type')
plt.xlabel('Operator Type')
plt.ylabel('CDMs Per Year')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../Plots/TotalCDMsByOperatorType.png', dpi=300, bbox_inches='tight')
plt.show()


# Individual plot for "CDMs Per Week by Operator Type"
plt.figure(figsize=(8, 6))
colors = [operator_type_colors[operator] for operator in operator_type_counts_per_week.keys()]
plt.bar(operator_type_counts_per_week.keys(), operator_type_counts_per_week.values(), color=colors)
plt.title('CDMs Per Week by Operator Type')
plt.xlabel('Operator Type')
plt.ylabel('CDMs Per Week')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../Plots/TotalCDMsPerWeekByOperatorType.png', dpi=300, bbox_inches='tight')
plt.show()