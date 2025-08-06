import sqlite3
import csv
import requests
import random
import time
import json

# Load old apple_ids.csv
print("📂 Loading existing Apple IDs...")
existing_ids = set()
try:
    with open("../apple_ids.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) > 0:
                existing_ids.add(row[0].strip())
    print(f"✅ Loaded {len(existing_ids)} existing IDs")
except FileNotFoundError:
    print("⚠️ apple_ids.csv not found, starting fresh")


# Load itunesIds from SQLite DB
print("🗄️ Loading iTunes IDs from database...")
conn = sqlite3.connect("podcastindex_feeds.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT itunesId FROM podcasts 
    WHERE itunesId IS NOT NULL 
      AND TRIM(itunesId) != '' 
      AND itunesId != '0'
""")
db_ids = {str(row[0]).strip() for row in cursor.fetchall()}
conn.close()
print(f"✅ Loaded {len(db_ids)} IDs from database")


# Determine new IDs
new_ids = list(existing_ids - db_ids)
print(f"🔍 Total new IDs to check: {len(new_ids)}")


# Enhanced User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]


def get_random_headers(prev=None):
    """Get random headers, ensuring different from previous"""
    max_attempts = 10
    attempts = 0
    
    while attempts < max_attempts:
        ua = random.choice(USER_AGENTS)
        headers = {
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        if prev is None or headers["User-Agent"] != prev.get("User-Agent"):
            return headers
        attempts += 1
    
    # If we can't find a different one, just return a random one
    return headers


def is_valid_itunes_id(itunes_id, prev_headers, retries=3):
    """Check if iTunes ID is valid with retry logic"""
    url = "https://itunes.apple.com/lookup"
    params = {"id": itunes_id, "entity": "podcast"}
    
    for attempt in range(retries):
        try:
            headers = get_random_headers(prev_headers)
            
            # Add random delay to avoid rate limiting
            if attempt > 0:
                time.sleep(random.uniform(2, 5))
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=10,  # Increased timeout
                allow_redirects=True
            )
            
            # Check if request was successful
            if response.status_code == 200:
                try:
                    data = response.json()
                    result_count = data.get("resultCount", 0)
                    
                    # Additional validation - check if it's actually a podcast
                    if result_count > 0:
                        results = data.get("results", [])
                        if results:
                            # Check if it's a podcast (not music, app, etc.)
                            first_result = results[0]
                            kind = first_result.get("kind", "")
                            wrapper_type = first_result.get("wrapperType", "")
                            
                            # Valid podcast indicators
                            is_podcast = (
                                kind == "podcast" or 
                                wrapper_type == "track" and 
                                first_result.get("primaryGenreName") in ["Podcasts", "Arts", "Business", "Comedy", "Education", "Fiction", "Government", "Health & Fitness", "History", "Kids & Family", "Leisure", "Music", "News", "Religion & Spirituality", "Science", "Society & Culture", "Sports", "Technology", "True Crime", "TV & Film"]
                            )
                            
                            if is_podcast:
                                return True, headers, f"Valid podcast: {first_result.get('collectionName', 'Unknown')}"
                            else:
                                return False, headers, f"Not a podcast: {kind}/{wrapper_type}"
                    
                    return False, headers, f"No results found (resultCount: {result_count})"
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error for {itunes_id} (attempt {attempt + 1}): {e}")
                    if attempt == retries - 1:
                        return False, headers, f"JSON decode error: {e}"
                    continue
                    
            elif response.status_code == 429:
                print(f"⚠️ Rate limited for {itunes_id} (attempt {attempt + 1}), waiting...")
                time.sleep(random.uniform(5, 10))
                continue
            else:
                print(f"⚠️ HTTP {response.status_code} for {itunes_id} (attempt {attempt + 1})")
                if attempt == retries - 1:
                    return False, headers, f"HTTP {response.status_code}"
                continue
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout for {itunes_id} (attempt {attempt + 1})")
            if attempt == retries - 1:
                return False, headers if 'headers' in locals() else None, "Timeout"
            continue
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request error for {itunes_id} (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                return False, headers if 'headers' in locals() else None, f"Request error: {e}"
            continue
            
        except Exception as e:
            print(f"⚠️ Unexpected error for {itunes_id} (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                return False, headers if 'headers' in locals() else None, f"Unexpected error: {e}"
            continue
    
    return False, None, "All retries failed"

# Initialize tracking variables
valid_ids = []
invalid_ids = []
failed_ids = []

# Open CSV files for writing
print(f"\n🚀 Starting validation of {len(new_ids)} IDs...")

with open("new_apple_ids_valid.csv", "w", encoding="utf-8", newline="") as valid_file, \
     open("new_apple_ids_invalid.csv", "w", encoding="utf-8", newline="") as invalid_file, \
     open("new_apple_ids_failed.csv", "w", encoding="utf-8", newline="") as failed_file:
    
    valid_writer = csv.writer(valid_file)
    invalid_writer = csv.writer(invalid_file)
    failed_writer = csv.writer(failed_file)
    
    # Write headers
    valid_writer.writerow(["itunes_id", "podcast_name"])
    invalid_writer.writerow(["itunes_id", "reason"])
    failed_writer.writerow(["itunes_id", "error"])
    
    prev_headers = None
    
    for idx, apple_id in enumerate(new_ids, 1):
        print(f"\n📊 Progress: {idx}/{len(new_ids)} ({idx/len(new_ids)*100:.1f}%)")
        print(f"🔍 Checking ID: {apple_id}")
        
        is_valid, prev_headers, message = is_valid_itunes_id(apple_id, prev_headers)
        
        if is_valid:
            print(f"✅ VALID: {apple_id} - {message}")
            valid_writer.writerow([apple_id, message.replace("Valid podcast: ", "")])
            valid_ids.append(apple_id)
        elif "error" in message.lower() or "timeout" in message.lower() or "failed" in message.lower():
            print(f"🔄 FAILED: {apple_id} - {message}")
            failed_writer.writerow([apple_id, message])
            failed_ids.append(apple_id)
        else:
            print(f"❌ INVALID: {apple_id} - {message}")
            invalid_writer.writerow([apple_id, message])
            invalid_ids.append(apple_id)
        
        # Flush files periodically
        if idx % 10 == 0:
            valid_file.flush()
            invalid_file.flush()
            failed_file.flush()
            print(f"💾 Progress saved - Valid: {len(valid_ids)}, Invalid: {len(invalid_ids)}, Failed: {len(failed_ids)}")
        
        # Random delay between requests
        delay = random.uniform(1, 3)
        time.sleep(delay)

# Final summary
print(f"\n🎉 VALIDATION COMPLETE!")
print(f"📊 SUMMARY:")
print(f"   ✅ Valid IDs: {len(valid_ids)}")
print(f"   ❌ Invalid IDs: {len(invalid_ids)}")
print(f"   🔄 Failed checks: {len(failed_ids)}")
print(f"   📋 Total processed: {len(valid_ids) + len(invalid_ids) + len(failed_ids)}")
print(f"\n📁 OUTPUT FILES:")
print(f"   📝 Valid IDs: new_apple_ids_valid.csv")
print(f"   📝 Invalid IDs: new_apple_ids_invalid.csv")
print(f"   📝 Failed checks: new_apple_ids_failed.csv")

if failed_ids:
    print(f"\n⚠️ NOTE: {len(failed_ids)} IDs failed due to network/API issues.")
    print("   Consider re-running these IDs later.")