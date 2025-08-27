import requests
import gzip
import io
import csv
from bs4 import BeautifulSoup
from datetime import datetime

# Path to existing IDs CSV
EXISTING_CSV = "../apple_ids.csv"

# File to save new IDs
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
DIFFERENT_FILE = f"different_{timestamp}.txt"

# Apple sitemap index
INDEX_URL = "https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml"


def load_existing_ids():
    """Load old IDs from CSV into a set"""
    existing_ids = set()
    try:
        with open(EXISTING_CSV, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # skip empty
                    existing_ids.add(row[0])
    except FileNotFoundError:
        print("⚠️ Existing CSV not found. Starting fresh.")
    return existing_ids


def get_gz_links_from_index(xml_url):
    """Fetch sitemap index and extract .gz links"""
    print(f"📥 Fetching sitemap index: {xml_url}")
    r = requests.get(xml_url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "xml")
    gz_links = [loc.text for loc in soup.find_all("loc") if loc.text.endswith(".gz")]
    print(f"📄 Found {len(gz_links)} .gz files")
    return gz_links


def extract_ids_from_gz(gz_url):
    """Download and extract podcast IDs from .gz"""
    try:
        print(f"🔽 Downloading: {gz_url}")
        r = requests.get(gz_url, timeout=20)
        r.raise_for_status()
        with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as f:
            content = f.read().decode("utf-8")
        soup = BeautifulSoup(content, "xml")
        ids = set()

        # Apple podcast URLs look like https://podcasts.apple.com/podcast/id123456789
        for loc in soup.find_all("loc"):
            url = loc.text.strip()
            if "id" in url:
                try:
                    podcast_id = url.split("id")[-1]
                    ids.add(podcast_id)
                except Exception:
                    continue
        print(f"✅ Extracted {len(ids)} IDs")
        return ids
    except Exception as e:
        print(f"❌ Failed to extract {gz_url}: {e}")
        return set()


def main():
    existing_ids = load_existing_ids()
    print(f"📂 Loaded {len(existing_ids)} existing IDs")

    gz_links = get_gz_links_from_index(INDEX_URL)

    all_new_ids = set()

    for gz in gz_links:
        ids = extract_ids_from_gz(gz)
        new_ids = ids - existing_ids
        if new_ids:
            print(f"➕ Found {len(new_ids)} new IDs in {gz}")
            all_new_ids.update(new_ids)

    # Save new IDs to text file
    if all_new_ids:
        with open(DIFFERENT_FILE, "w", encoding="utf-8") as f:
            for nid in sorted(all_new_ids):
                f.write(nid + "\n")
        print(f"💾 Saved {len(all_new_ids)} new IDs to {DIFFERENT_FILE}")
    else:
        print("✅ No new IDs found.")


if __name__ == "__main__":
    main()

# import io
# from bs4 import BeautifulSoup
# import re
# import gzip
# import sys
# import requests
# import hashlib
# import time
# import csv
# import os
# from datetime import datetime

# sys.path.append(os.path.abspath("..")) 
# import password

# API_KEY = password.API_KEY
# API_SECRET = password.API_SECRET

# COUNTRY_CODES= [
# 'dz', 'ao', 'am', 'az', 'bh', 'bj', 'bw', 'bn', 'bf', 'cm', 'cv', 'td', 'ci', 'cd', 'eg',
# 'sz', 'ga', 'gm', 'gh',
# 'gw', 'in', 'iq', 'il', 'jo', 'ke', 'kw', 'lb', 'lr', 'ly', 'mg',
# 'mw', 'ml', 'mr',
# 'mu', 'ma', 'mz','na',
#  'ne', 'ng', 'om', 'qa', 'cg',
#  'rw', 'sa', 'sn',
# 'sc', 'sl', 'za', 'lk', 'tj', 'tz', 'tn', 'tm',
# 'ae', 'ug', 'ye', 'zm',
# 'zw', 'au', 'bt',
# 'kh', 'cn', 'fj', 'hk', 'id', 'jp', 'kz', 'kr', 'kg', 'la',
#  'mo', 'my', 'mv', 'fm',
#   'mn',
# 'mm', 'np', 'nz',
#  'pg', 'ph', 'sg', 'sb', 'tw', 'th', 'to', 'uz', 'vu', 'vn',
#   'at', 'by',
# 'be', 'ba', 'bg', 'hr', 'cy', 'cz',
#  'dk', 'ee', 'fi',
#  'fr', 'ge', 'de', 'gr', 'hu', 'is',
# 'ie', 'it', 'xk', 'lv', 'lt', 'lu', 'mt', 'md', 'me', 'nl', 'mk', 'no', 'pl', 'pt', 'ro',
# 'ru', 'rs', 'sk', 'si', 'es', 'se', 'ch', 'tr', 'ua', 'gb', 'ai', 'ag', 'ar', 'bs', 'bb',
# 'bz',
# 'bm', 'bo', 'br', 'vg', 'ky', 'cl', 'co', 'cr', 'dm', 'do', 'ec', 'sv', 'gd', 'gt',
# 'gy', 'hn', 'jm', 'mx', 'ms', 'ni', 'pa', 'py', 'pe', 'kn', 'lc', 'vc', 'sr', 'tt', 'tc',
# 'uy', 've','ca', 'us']

# existing_csv = "../apple_ids.csv"     # The old/existing IDs you already have
# new_ids_file = "new_ids_{timestamp}.csv"             # IDs you just scraped in your main script
# output_file = "new_unique_ids.txt"    # Output: only IDs that are new
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# missing_gz_files = set()

# def get_gz_links_from_index(xml_url):
#     try:
#         print(f"📥 Fetching sitemap index: {xml_url}")
#         r = requests.get(xml_url, timeout=10)
#         r.raise_for_status()
#         soup = BeautifulSoup(r.text, "xml")
#         gz_links = [loc.text for loc in soup.find_all("loc") if loc.text.endswith(".gz")]
#         print(f"📄 Found {len(gz_links)} .gz files")
#         return gz_links
#     except requests.exceptions.HTTPError as e:
#         if r.status_code == 404:  # file not found
#             print(f"⚠️ Missing file: {xml_url}")
#             missing_gz_files.add(xml_url)  # save it for retry later
#         else:
#             print(f"❌ HTTP error fetching sitemap index: {e}")
#         return []
#     except Exception as e:
#         print(f"❌ Error fetching sitemap index: {e}")
#         return []


# def retry_missing_files():
#     """Try fetching missing files once more."""
#     if not missing_gz_files:
#         print("✅ No missing files to retry.")
#         return []

#     print(f"🔄 Retrying {len(missing_gz_files)} missing files...")
#     retry_results = []
#     failed_still = set()

#     for url in list(missing_gz_files):
#         try:
#             r = requests.get(url, timeout=10)
#             r.raise_for_status()
#             retry_results.append(url)
#             missing_gz_files.remove(url)  # success, remove from missing set
#             print(f"✅ Successfully fetched on retry: {url}")
#         except Exception as e:
#             print(f"❌ Still failing: {url} | Error: {e}")
#             failed_still.add(url)

#     return retry_results, failed_still


# # === Extract podcast IDs directly from .gz file contents ===
# def extract_ids_from_gz(gz_url):
#     ids = set()
#     try:
#         print(f"➡️ Downloading .gz: {gz_url}")
#         r = requests.get(gz_url, timeout=15)
#         r.raise_for_status()
#         with gzip.open(io.BytesIO(r.content), "rt", encoding="utf-8") as f:
#             content = f.read()
#             found = re.findall(r'/id(\d{8,})', content)
#             ids.update(found)
#         print(f"   🎯 Found {len(ids)} IDs in this file")
#     except Exception as e:
#         print(f"❌ Error processing {gz_url}: {e}")
#     return ids


# def save_ids_to_csv(ids, filename):
#     with open(filename, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["itunesId"])
#         for pid in sorted(ids):
#             writer.writerow([pid])
#     print(f"✅ Saved {len(ids)} IDs to {filename}")


# # --------------------------------------
# # 4. Compare new IDs with old IDs
# # --------------------------------------
# def compare_ids(old_csv, new_csv):
#     old_ids = set()
#     new_ids = set()

#     # Load old
#     try:
#         with open(old_csv, "r", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             next(reader, None)  # skip header if present
#             for row in reader:
#                 if row:
#                     old_ids.add(row[0].strip())
#     except FileNotFoundError:
#         print(f"⚠️ Old file {old_csv} not found, treating as empty")

#     # Load new
#     with open(new_csv, "r", encoding="utf-8") as f:
#         reader = csv.reader(f)
#         next(reader, None)  # skip header
#         for row in reader:
#             if row:
#                 new_ids.add(row[0].strip())

#     unique_ids = new_ids - old_ids
#     print(f"✨ Found {len(unique_ids)} new unique IDs")
#     return unique_ids


# # --------------------------------------
# # 5. Validate IDs
# # --------------------------------------
# def get_pi_headers():
#     auth_time = str(int(time.time()))
#     auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()
#     return {
#         "User-Agent": "MillionPodcastCrawler/1.0",
#         "X-Auth-Key": API_KEY,
#         "X-Auth-Date": auth_time,
#         "Authorization": auth_hash
#     }

# def check_apple_lookup(itunes_id):
#     url = f"https://itunes.apple.com/lookup?id={itunes_id}"
#     try:
#         r = requests.get(url, timeout=5)
#         if r.status_code == 200:
#             data = r.json()
#             return data.get("resultCount", 0) > 0
#     except requests.RequestException:
#         pass
#     return False

# def check_podcastindex(itunes_id):
#     url = f"https://api.podcastindex.org/api/1.0/add/byitunesid?id={itunes_id}"
#     try:
#         r = requests.post(url, headers=get_pi_headers(), timeout=5)
#         if r.status_code == 200:
#             data = r.json()
#             return bool(data.get("status") or data.get("feedId"))
#     except requests.RequestException:
#         pass
#     return False

# def check_apple_store(itunes_id, timeout=5, sleep_time=0.5):
#     base_url = "https://podcasts.apple.com/{country}/podcast/id{pid}"
#     for country in COUNTRY_CODES:
#         url = base_url.format(country=country, pid=itunes_id)
#         try:
#             r = requests.head(url, timeout=timeout, allow_redirects=True)
#             if r.status_code == 200:
#                 return True
#         except requests.RequestException:
#             pass
#         time.sleep(sleep_time)
#     return False

# def validate_ids(ids, valid_file="valid_ids.txt", invalid_file="invalid_ids.txt"):
#     valid, invalid = set(), set()

#     with open(valid_file, "w", encoding="utf-8") as vf, open(invalid_file, "w", encoding="utf-8") as inf:
#         for pid in ids:
#             print(f"🔍 Checking {pid}...")
#             if check_apple_lookup(pid) or check_podcastindex(pid) or check_apple_store(pid):
#                 valid.add(pid)
#                 vf.write(pid + "\n")
#                 print(f"✅ {pid} VALID")
#             else:
#                 invalid.add(pid)
#                 inf.write(pid + "\n")
#                 print(f"❌ {pid} INVALID")

#     print(f"\n📂 {len(valid)} valid IDs saved to {valid_file}")
#     print(f"📂 {len(invalid)} invalid IDs saved to {invalid_file}")
#     return valid, invalid


# # --------------------------------------
# # Example usage
# # --------------------------------------
# if __name__ == "__main__":
#     # Example flow
#     gz_url = "https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml"

#     # Step 1: Fetch sitemap XML and grab first gz link
#     r = requests.get(gz_url, timeout=10)
#     soup = BeautifulSoup(r.text, "xml")
#     first_gz = [loc.text for loc in soup.find_all("loc") if loc.text.endswith(".gz")][0]

#     # Step 2: Download & extract
#     gz_bytes = get_gz_links_from_index(first_gz)
#     ids = extract_ids_from_gz(gz_bytes)

#     # Step 3: Save to CSV
#     save_ids_to_csv(ids, new_ids_file)

#     # Step 4: Compare with old
#     unique = compare_ids(existing_csv, new_ids_file)

#     # Step 5: Validate
#     validate_ids(unique)