# import requests
# import password
# import json

# # Replace with your own Spotify API credentials
# CLIENT_ID = password.CLIENT_ID
# CLIENT_SECRET = password.CLIENT_SECRET

# # The podcast ID you want to look up (from open.spotify.com/show/...)
# SHOW_ID = "34ETtoDYjZtR6ORTJVFvi8"  # example

# # Step 1 — Get an access token
# auth_response = requests.post(
#     "https://accounts.spotify.com/api/token",
#     data={"grant_type": "client_credentials"},
#     auth=(CLIENT_ID, CLIENT_SECRET)
# )
# auth_response.raise_for_status()
# access_token = auth_response.json()["access_token"]

# # Step 2 — Call the Spotify API for the show
# headers = {"Authorization": f"Bearer {access_token}"}
# url = f"https://api.spotify.com/v1/shows/{SHOW_ID}"

# response = requests.get(url, headers=headers)
# response.raise_for_status()
# data = response.json()

# pretty_json = json.dumps(data, indent=4)

# # Add a decorative star before printing
# print("*" * 30)  # Prints 30 asterisks
# print(pretty_json)
# print("*" * 30)

# # Step 3 — Print basic details
# print("Podcast Name:", data["name"])
# print("Publisher:", data["publisher"])
# print("Description:", data["description"])
# print("Image URL:", data["images"][0]["url"] if data["images"] else "No image")
# print("Total Episodes:", data["total_episodes"])

import requests
import time
import logging

# Setup logging to file
logging.basicConfig(filename="error.txt", level=logging.ERROR, 
                    format="%(asctime)s - %(message)s")

URL = "https://podcastcharts.byspotify.com/api/charts/top?region=gb"
timeout_seconds = 10

def make_request(req_num):
    try:
        r = requests.get(URL, timeout=timeout_seconds)
        if r.status_code != 200:
            logging.error(f"Request #{req_num} failed with status code: {r.status_code}")
        return r.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Request #{req_num} encountered error: {e}")
        return None

def find_rate_limit():
    req_count = 0
    start_time = time.time()
    
    while True:
        req_count += 1
        status = make_request(req_count)
        elapsed = time.time() - start_time
        print(f"[REQ #{req_count}] Status: {status} | Time elapsed: {elapsed:.2f}s")

        if status == 429:
            print(f"\n🚫 Rate limit hit at request #{req_count} after {elapsed:.2f} seconds.")
            break

        # small delay so we don't burn the limit too fast
        

    print(f"\nTotal successful requests before rate limit: {req_count - 1}")
    print("All errors are logged in error_log.txt")

if __name__ == "__main__":
    find_rate_limit()
