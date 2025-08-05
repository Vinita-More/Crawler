import time
import hashlib
import requests
import sys
import os

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

# Example API call
def get_recent_feeds():
    url = "https://api.podcastindex.org/api/1.0/recent/feeds"
    headers = generate_headers()
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Extract all itunesIds
        feeds = data.get('feeds', [])
        itunes_ids = []

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
