# To check for new appleids from podcastIndex.org (using API)
import time
import password
import hashlib
import requests

# 🔐 Replace these with your real values
API_KEY = password.API_KEY
API_SECRET = password.API_SECRET

# ⏱️ Get current Unix time
auth_date = str(int(time.time()))

message = API_KEY + API_SECRET + auth_date
signature = hashlib.sha1(message.encode("utf-8")).hexdigest()

# 📨 Required headers
headers = {
    "User-Agent": "TestPodcastApp/1.0",
    "X-Auth-Key": API_KEY,
    "X-Auth-Date": auth_date,
    "Authorization": signature
}

# 🎯 PodcastIndex test endpoint
url = "https://api.podcastindex.org/api/1.0/recent/feeds"

# 📡 Send GET request
response = requests.get(url, headers=headers)
unique_podcasts = {}

def is_valid_apple_id(val):
    try:
        return int(val) > 0
    except (TypeError, ValueError):
        return False


if response.status_code == 200:
    feeds = response.json()["feeds"]
    for feed in feeds:
        apple_id = feed.get("itunesId")
        if is_valid_apple_id(apple_id):
            if apple_id not in unique_podcasts:
                unique_podcasts[apple_id] = {"itunesId": apple_id}

       # Save to file
    with open("unique_podcasts.txt", "w", encoding="utf-8") as f:
        for podcast in unique_podcasts.values():
            f.write(f"{podcast['itunesId']}\n")

    print("✅ Saved unique podcasts with Apple IDs to 'unique_podcasts.txt'")
else:
    print("Error:", response.text)
