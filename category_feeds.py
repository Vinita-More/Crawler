import time
import hashlib
import requests
import password
import csv

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

all_ids = set()

# Auth headers
auth_time = str(int(time.time()))
auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()

headers = {
    "User-Agent": "MillionPodcastCrawler/1.0",
    "X-Auth-Key": API_KEY,
    "X-Auth-Date": auth_time,
    "Authorization": auth_hash
}

# Iterate over categories
for category in CATEGORIES:
    url = f"https://api.podcastindex.org/api/1.0/search/byterm?q={category}&max=100"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        feeds = response.json().get("feeds", [])
        for feed in feeds:
            apple_id = feed.get("itunesId")
            if isinstance(apple_id, int) or (isinstance(apple_id, str) and apple_id.isdigit()):
                all_ids.add(str(apple_id))

        print(f"✅ Fetched {len(feeds)} feed ids from '{category}'")
    else:
        print(f"❌ Failed for {category}: {response.status_code} - {response.text}")

# Save all unique IDs into one file
with open("all_apple_ids.txt", "w", encoding="utf-8") as f:
    for id in sorted(all_ids):
        f.write(f"{id}\n")

print(f"📦 Saved {len(all_ids)} unique Apple IDs to 'all_apple_ids.txt'")


# Load existing Apple IDs from CSV
with open("apple_ids.csv", "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    existing_ids = {row[0].strip() for row in reader if row}  # Handle blank rows

# Load newly fetched Apple IDs from TXT
with open("all_apple_ids.txt", "r", encoding="utf-8") as txtfile:
    new_ids = {line.strip() for line in txtfile if line.strip()}

# Get IDs that are in new list but not in existing CSV
unique_ids = new_ids - existing_ids

# Print or save
print(f"🆕 Found {len(unique_ids)} new Apple IDs")

with open("new_unique_ids.txt", "w", encoding="utf-8") as out:
    for uid in sorted(unique_ids):
        out.write(uid + "\n")