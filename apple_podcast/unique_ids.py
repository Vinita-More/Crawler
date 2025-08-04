import time
import hashlib
import requests
import os
import csv
import sys

sys.path.append(os.path.abspath("..")) 
import password

API_KEY = password.API_KEY
API_SECRET = password.API_SECRET

CATEGORIES = [
    "After-Shows", "Alternative", "Animals", "Animation", "Arts", "Astronomy", "Automotive",
    "Aviation", "Baseball", "Basketball", "Books", "Business", "Careers", "Christianity",
    "Comedy", "Courses", "Cricket", "Daily News", "Design", "Documentary", "Drama",
    "Earth Sciences", "Education", "Entrepreneurship", "Fiction", "Film History", "Film Interviews",
    "Fitness", "Food", "Football", "Games", "Government", "Health & Fitness", "History", "Hobbies",
    "Hockey", "Home & Garden", "Hinduism", "How To", "Improv", "Islam", "Investing", "Islamic",
    "Jainism", "Judaism", "Kids & Family", "Language Learning", "Leisure", "Life Sciences",
    "Literature", "Management", "Marketing", "Mathematics", "Medicine", "Mental Health",
    "Music", "Music Commentary", "Music History", "Music Interviews", "Nature", "News",
    "News Commentary", "Non-Profit", "Nutrition", "Parenting", "Performing Arts", "Personal Journals",
    "Philosophy", "Physics", "Places & Travel", "Politics", "Relationships", "Religion & Spirituality",
    "Running", "Science", "Self-Improvement", "Sexuality", "Social Sciences", "Society & Culture",
    "Software How-To", "Spirituality", "Sports", "Sports News", "Stories for Kids", "Swimming",
    "TV & Film", "Technology", "Tennis", "Theater", "Training", "True Crime", "TV Reviews",
    "Video Games", "Visual Arts", "Volleyball", "Weather", "Wilderness", "Wrestling", "Yoga",
    "Christian", "Spiritual", "Nature Talks", "Music Business", "Finance", "Daily Life",
    "Pets", "DIY", "Outdoors", "Mindfulness", "Podcasts"
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_FILE = os.path.join(BASE_DIR, "apple_ids.csv")            # ← Your CSV file with known IDs
ALL_IDS_TXT = "all_unique_apple_ids.txt"     # ← Master list to store all fetched IDs
NEW_IDS_TXT = "new_unique_ids.txt"           # ← Output file for new IDs only

# Step 1: Load existing CSV file IDs into a set
existing_ids = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for cell in row:
                if cell.strip().isdigit():
                    existing_ids.add(cell.strip())

# Step 2: Load previously fetched IDs to avoid duplication in master file
stored_ids = set()
if os.path.exists(ALL_IDS_TXT):
    with open(ALL_IDS_TXT, "r", encoding="utf-8") as f:
        stored_ids = set(line.strip() for line in f if line.strip().isdigit())

# Step 3: Prepare API headers
auth_time = str(int(time.time()))
auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()
headers = {
    "User-Agent": "MillionPodcastCrawler/1.0",
    "X-Auth-Key": API_KEY,
    "X-Auth-Date": auth_time,
    "Authorization": auth_hash
}

# Step 4: Collect and compare Apple Podcast IDs
new_ids = set()
all_fetched_ids = set()

for category in CATEGORIES:
    print(f"🔍 Fetching category: {category}")
    url = f"https://api.podcastindex.org/api/1.0/search/byterm?q={category}&max=100"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        feeds = response.json().get("feeds", [])
        for feed in feeds:
            apple_id = feed.get("itunesId")
            if isinstance(apple_id, int) or (isinstance(apple_id, str) and str(apple_id).isdigit()):
                id_str = str(apple_id)
                all_fetched_ids.add(id_str)
                if id_str not in existing_ids and id_str not in stored_ids:
                    new_ids.add(id_str)
    else:
        print(f"❌ Failed for {category}: {response.status_code} - {response.text}")

# Step 5: Append all fetched IDs to master file (only new to file)
with open(ALL_IDS_TXT, "a", encoding="utf-8") as f:
    for id_str in sorted(all_fetched_ids - stored_ids):
        f.write(f"{id_str}\n")

# Step 6: Write new unique IDs (not in CSV) to separate file
if new_ids:
    with open(NEW_IDS_TXT, "w", encoding="utf-8") as f:
        for id_str in sorted(new_ids):
            f.write(f"{id_str}\n")
    print(f"✅ Found and saved {len(new_ids)} new unique Apple IDs to '{NEW_IDS_TXT}'")
else:
    print("ℹ️ No new Apple IDs found compared to CSV.")
