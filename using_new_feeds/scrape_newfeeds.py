import time
import hashlib
import requests
import sys
import os
import csv

# Add parent directory to Python path
sys.path.append(os.path.abspath('..'))

import password  # your password.py must have API_KEY and API_SECRET

API_KEY = password.API_KEY
API_SECRET = password.API_SECRET

def generate_headers():
    current_time = str(int(time.time()))
    data_to_hash = API_KEY + API_SECRET + current_time
    auth_hash = hashlib.sha1(data_to_hash.encode('utf-8')).hexdigest()

    headers = {
        'User-Agent': 'MyPodcastApp/1.0',  # any custom app name
        'X-Auth-Date': current_time,
        'X-Auth-Key': API_KEY,
        'Authorization': auth_hash
    }
    return headers

itunes_ids = []

# Example API call
def get_recent_feeds():
    url = "https://api.podcastindex.org/api/1.0/recent/feeds"
    headers = generate_headers()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Extract all itunesIds
        feeds = data.get('feeds', [])
        

        for feed in feeds:
            itunes_id = feed.get('itunesId')
            if itunes_id:  # Skip if None or missing
                itunes_ids.append(itunes_id)

        print(f"Total iTunes IDs found: {len(itunes_ids)}")
        for i, id in enumerate(itunes_ids, start=1):
            print(f"{i}. {id}")
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)
get_recent_feeds()

old_data = "../apple_ids.csv"

# with open(old_data, "r", encoding="utf-8") as csvfile:
#     reader = csv.reader(csvfile)
#     existing_ids = {row[0].strip() for row in reader if row}

with open(old_data, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    existing_ids = [row[0].strip() for row in reader if row]


# Convert new itunes_ids to set of strings
itunes_id_set = set(str(i).strip() for i in itunes_ids)

# Get new IDs that are NOT in the CSV file
new_ids = itunes_id_set - set(existing_ids)

# Output the result
print(f"Number of NEW IDs not in CSV: {len(new_ids)}")
if new_ids:
    print("These iTunes IDs are new (not in CSV):")
    for i in new_ids:
        print(i)
else:
    print("No new IDs found.")
# new_ids = set(itunes_ids) - set(existing_ids)
# print(f"number of new ids {len(new_ids)}" )
# for i in new_ids:
#     print(i)