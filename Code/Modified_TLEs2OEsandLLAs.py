import numpy as np
import ephem
import datetime
import csv
from pathlib import Path
import matplotlib.dates
from tqdm import tqdm

# Define constants
G = 6.67408 * 10**-11  # Gravitational constant in m^3 kg^-1 s^-2
M = 5.972 * 10**24    # Mass of the Earth in kg
Re = 6.371 * 10**6    # Radius of the Earth in m

# Helper functions
def dms(degrees):
    return float(degrees)

def compute_altitude(tle_rec, timestamp):
    """Compute the altitude of a satellite using its TLE record and a specific timestamp."""
    tle_rec.compute(timestamp)
    subsatellitepoint = ephem.Observer()
    subsatellitepoint.date = timestamp
    subsatellitepoint.lon = tle_rec.sublong
    subsatellitepoint.lat = tle_rec.sublat
    tle_rec.compute(subsatellitepoint)
    return tle_rec.range

def nearest(items, pivot):
    """Find the item in `items` closest to `pivot`."""
    return min(items, key=lambda x: abs(x - pivot))

# Create output directory if it does not exist
Path("../Data/").mkdir(parents=True, exist_ok=True)

# Read the input file
input_file = "../Data/NewCDMsSet.csv"
output_file = "../Data/output.csv"

with open(input_file, "r", encoding='utf-8-sig') as infile, open(output_file, "w", newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["SAT1_ALTITUDE_TCA", "SAT2_ALTITUDE_TCA"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()


    for row in tqdm(reader, desc="Processing rows", unit="row"):
        sat1 = row["SAT1_OBJECT_DESIGNATOR"]
        sat2 = row["SAT2_OBJECT_DESIGNATOR"]
        tca = datetime.datetime.strptime(row["TCA"], "%Y-%m-%d %H:%M:%S.%f")

        def get_closest_tle(satcat, tca):
            """Get the TLE lines closest to the TCA for a given satellite."""
            try:
                with open(f'../Data/TLEs/{satcat}.txt', 'r') as tle_file:
                    tle_lines = tle_file.readlines()
                    epochs = []
                    tle_pairs = []

                    for i in range(0, len(tle_lines), 2):
                        line1, line2 = tle_lines[i].strip(), tle_lines[i + 1].strip()
                        year = int("20" + line1[18:20]) if int(line1[18:20]) < 57 else int("19" + line1[18:20])
                        day_of_year = float(line1[20:32])
                        epoch = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
                        epochs.append(epoch)
                        tle_pairs.append((line1, line2))

                    closest_epoch = nearest(epochs, tca)
                    closest_index = epochs.index(closest_epoch)
                    return tle_pairs[closest_index]
            except (FileNotFoundError, IndexError):
                return None, None

        try:
            # Find TLE closest to TCA for SAT1
            line1, line2 = get_closest_tle(sat1, tca)
            if line1 and line2:
                sat1_rec = ephem.readtle(sat1, line1, line2)
                sat1_rec.compute(matplotlib.dates.num2date(matplotlib.dates.date2num(tca)))
                sat1_alt = compute_altitude(sat1_rec, tca)
            else:
                sat1_alt = "N/A"
        except Exception:
            sat1_alt = "N/A"

        try:
            # Find TLE closest to TCA for SAT2
            line1, line2 = get_closest_tle(sat2, tca)
            if line1 and line2:
                sat2_rec = ephem.readtle(sat2, line1, line2)
                sat2_rec.compute(matplotlib.dates.num2date(matplotlib.dates.date2num(tca)))
                sat2_alt = compute_altitude(sat2_rec, tca)
            else:
                sat2_alt = "N/A"
        except Exception:
            sat2_alt = "N/A"

        # Append calculated altitudes to the row
        row["SAT1_ALTITUDE_TCA"] = sat1_alt
        row["SAT2_ALTITUDE_TCA"] = sat2_alt

        # Write updated row to output
        writer.writerow(row)

print(f"Processed data written to {output_file}")