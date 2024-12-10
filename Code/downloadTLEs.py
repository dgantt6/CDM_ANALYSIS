import spacetrack.operators as op
from spacetrack import SpaceTrackClient
import datetime as d
from time import sleep
import csv
from pathlib import Path
import pandas as pd
import os

# Ensure output directory exists. If not, make it.
output_dir = "../Data/TCA_SATCATS"
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Check whether ./Data/TLEs/ exists. If not, make it.
path = '../../Data/TLEs/'
Path(path).mkdir(parents=True, exist_ok=True)


# Prompt user for Space-Track log-in credentials
print("Log in to using your Space-Track.org account credentials.\n")
st_email = input("Email: ") # UNCOMMENT THESE
st_pass = input("Password: ") # UNCOMMENT THESE

# Log in to Space-Track using your email and password
st = SpaceTrackClient(identity=st_email, password=st_pass)


# Make a list of all the satcats in Data/satcats.csv
satcats = []

with open("../Data/satcats.csv", encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        satcats.append(row[0])

# determine TCA start date and end date
earliest_tca = None
latest_tca = None
filename = input('Add the file path for the full data file:')
with open(filename, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Parse the TCA date from the row
        tca_datetime = dt.datetime.fromisoformat(row['TCA'])

        # Update earliest and latest TCA
        if earliest_tca is None or tca_datetime < earliest_tca:
            earliest_tca = tca_datetime
        if latest_tca is None or tca_datetime > latest_tca:
            latest_tca = tca_datetime

study_start = earliest_tca.date()
study_end = latest_tca.date()
date_range = pd.date_range(start=study_start, end=study_end)
tca_dates = [(date - dt.timedelta(days=14), date + dt.timedelta(days=14)) for date in date_range]

# Print the results
print(f"Earliest TCA: {study_start}")
print(f"Latest TCA: {study_end}")

drange = op.inclusive_range(study_start, study_end)

i = 0
while i < len(satcats):
    try:
        if os.path.exists('../Data/TLEs/'+str(satcats[i])+'.txt'):
            print('Skipping' + str(satcats[i]))
        else:
            print('Downloading' + str(satcats[i]))
            with open('../Data/TLEs/'+str(satcats[i])+'.txt','w') as f:
                f.write(st.tle(norad_cat_id=satcats[i], epoch=drange, orderby='epoch desc', format='gp_history'))
                f.close()
            print("Printed file: " + str(satcats[i]) + ".txt.")
            for j in range(26):
                if j < 13:
                    print("*"*(j+1))
                    sleep(0.5)
                else:
                    print("*"*(26-j))
                    sleep(0.5)
        i+=1
    except:
        print('Lowkey Failed')
        os.remove('../Data/TLEs/'+str(satcats[i])+'.txt')
        sleep(15)

