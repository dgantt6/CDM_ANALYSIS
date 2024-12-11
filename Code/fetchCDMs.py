import requests
import csv
from datetime import datetime

CDM_type = input("Do you want to fetch public data? (y/n): ")

def parse_date(date_string):
    """Helper function to parse date strings with microseconds to datetime objects."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return None

if CDM_type == 'y' :
    # Prompt user for Space-Track log-in credentials
    print("Log in to using your Space-Track.org account credentials.\n")
    st_email = input("Email: ")
    st_pass = input("Password: ")

    base_url = "https://www.space-track.org/ajaxauth/login"
    login_data = {
        'identity': st_email,
        'password': st_pass,
    }
    session = requests.Session()
    response = session.post(base_url, data=login_data)


    if response.status_code == 200:
        print("Authenticated successfully")
        print("Fetching CDM_type data...")
        # Define the API endpoint for CDM_type collision data messages (CDM)
        cdm_public_url = "https://www.space-track.org/basicspacedata/query/class/cdm_public"

        # Perform the GET request to fetch CDM data
        cdm_response = session.get(cdm_public_url)

        # Check if the GET request was successful
        if cdm_response.status_code == 200:
            print("CDM data fetched successfully")
            # Print the JSON response
            data = cdm_response.json()
            print(data)

            satellite_ids = set()  # Use a set to ensure uniqueness

            for cdm in data:
                sat_id_1 = cdm.get('SAT_1_ID')
                sat_id_2 = cdm.get('SAT_2_ID')

                if sat_id_1:
                    satellite_ids.add(sat_id_1)
                if sat_id_2:
                    satellite_ids.add(sat_id_2)

            with open('../Data/satcats.csv', mode='w', newline='', encoding='utf-8') as f:

                writer = csv.writer(f)
                writer.writerow(['ID'])
                for satellite_id in sorted(satellite_ids):  # Ensuring sorted order for consistency
                    writer.writerow([satellite_id])
        else:
                print("Failed to fetch CDM data. CDM request was not made.")
    else:
        print(f"Authentication failed. Status code: {response.status_code}")

elif CDM_type == 'n':
    print("Fetching private data...")
    cdm_filename = input("Enter the full path to the downloaded private CSV file: ")
    satellite_ids = set()  # Use a set to ensure uniqueness
    all_rows = []
    conjunction_data = {}

    try:
        with open(cdm_filename, mode='r', newline='', encoding='utf-8') as file:
            print('Opening and parsing file...')
            data = csv.DictReader(file)
            headers = data.fieldnames

            # Read and process the data
            for cdm in data:
                sat_id_1 = cdm.get('SAT1_OBJECT_DESIGNATOR')
                sat_id_2 = cdm.get('SAT2_OBJECT_DESIGNATOR')
                sat1_type = cdm.get('SAT1_OBJECT_TYPE')
                sat2_type = cdm.get('SAT2_OBJECT_TYPE')
                collision_prob = cdm.get('COLLISION_PROBABILITY')
                creation_date = parse_date(cdm.get('CREATION_DATE'))
                tca_date = parse_date(cdm.get('TCA'))

                # Ensure valid data and relevant payload information
                if (sat1_type == 'PAYLOAD' or sat2_type == 'PAYLOAD') and (
                        sat1_type != 'UNKNOWN' and sat2_type != 'UNKNOWN') and collision_prob != 'NULL':
                    # Create a key for unique conjunctions, considering same year, month, and day
                    conjunction_key = (frozenset([sat_id_1, sat_id_2]), tca_date.date())
                    satellite_ids.update([sat_id_1, sat_id_2])  # Add IDs to the satellite set

                    # Determine if this CDM is closer to TCA than the current best for the conjunction
                    if conjunction_key not in conjunction_data or (
                            creation_date and tca_date and abs((tca_date - creation_date).total_seconds()) <
                            abs((tca_date - parse_date(
                                conjunction_data[conjunction_key]['CREATION_DATE'])).total_seconds())):
                        conjunction_data[conjunction_key] = cdm  # Update the best CDM for this conjunction

            # Save satellite IDs
            with open('../Data/satcats.csv', mode='w', newline='', encoding='utf-8') as f:
                print('Opening satcats.csv')
                writer = csv.writer(f)
                for satellite_id in sorted(satellite_ids):  # Ensuring sorted order for consistency
                    writer.writerow([satellite_id])

            # Save filtered CDM data
            filename = '../Data/NewCDMsSet.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow(headers)
                for conjunction_key, cdm in conjunction_data.items():
                    csv_writer.writerow(cdm.values())


    except FileNotFoundError:
        print(f"The file at {cdm_filename} was not found. Please check the path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")