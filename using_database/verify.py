import sqlite3
import csv
import requests
import random
import time

# Load old apple_ids.csv
with open("../apple_ids.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    existing_ids = {row[0].strip() for row in reader if row}

# Load itunesIds from SQLite DB
conn = sqlite3.connect("podcastindex_feeds.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT itunesId FROM podcasts 
    WHERE itunesId IS NOT NULL 
      AND TRIM(itunesId) != '' 
      AND itunesId != '0'
""")
db_ids = {str(row[0]).strip() for row in cursor.fetchall()}

# Determine new IDs
new_ids = list(db_ids - existing_ids)
print(f"🔍 Total new IDs to check: {len(new_ids)}")

# List of 10 user-agent headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Android 11; Mobile; rv:89.0)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F)"
]

def get_random_headers(prev=None):
    # Ensure not the same as previous header
    headers = None
    while True:
        ua = random.choice(USER_AGENTS)
        headers = {"User-Agent": ua}
        if headers != prev:
            return headers

def is_valid_itunes_id(itunes_id, prev_headers):
    url = "https://itunes.apple.com/lookup"
    params = {"id": itunes_id, "entity": "podcast"}
    headers = get_random_headers(prev_headers)
    try:
        response = requests.get(url, params=params, headers=headers, timeout=1)
        data = response.json()
        return data.get("resultCount", 0) > 0, headers
    except Exception as e:
        print(f"⚠️ Error on {itunes_id}: {e}")
        return False, headers

# Open CSV for writing valid IDs
valid_ids = []
with open("new_apple_ids.csv", "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    prev_headers = None
    for idx, apple_id in enumerate(new_ids, 1):
        is_valid, prev_headers = is_valid_itunes_id(apple_id, prev_headers)
        if is_valid:
            print(f"{idx} ✅ Valid: {apple_id}")
            writer.writerow([apple_id])
            valid_ids.append(apple_id)
        else:
            print(f"{idx} ❌ Invalid or Failed: {apple_id}")
        time.sleep(1)

print(f"\n🎉 Finished. {len(valid_ids)} valid Apple IDs saved.")
