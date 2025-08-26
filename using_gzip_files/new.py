
import io
from bs4 import BeautifulSoup
import re
import gzip
import sys
import requests
import hashlib
import time
import csv
import os

sys.path.append(os.path.abspath("..")) 
import password

API_KEY = password.API_KEY
API_SECRET = password.API_SECRET


existing_csv = "../apple_ids.csv"     # The old/existing IDs you already have
new_ids_file = "new.txt"              # IDs you just scraped in your main script
output_file = "new_unique_ids.txt"    # Output: only IDs that are new

def load_existing_ids(csv_path):
    existing = set()
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # ignore blank rows
                    existing.add(row[0].strip())
        print(f"📂 Loaded {len(existing)} IDs from {csv_path}")
    except FileNotFoundError:
        print(f"⚠️ File not found: {csv_path}, treating as empty")
    return existing

# Apple country codes
COUNTRY_CODES = [
    'dz','ao','am','az','bh','bj','bw','bn','bf','cm','cv','td','ci','cd','eg','sz','ga','gm','gh',
    'gw','in','iq','il','jo','ke','kw','lb','lr','ly','mg','mw','ml','mr','mu','ma','mz','na',
    'ne','ng','om','qa','cg','rw','sa','sn','sc','sl','za','lk','tj','tz','tn','tm',
    'ae','ug','ye','zm','zw','au','bt','kh','cn','fj','hk','id','jp','kz','kr','kg','la',
    'mo','my','mv','fm','mn','mm','np','nz','pg','ph','sg','sb','tw','th','to','uz','vu','vn',
    'at','by','be','ba','bg','hr','cy','cz','dk','ee','fi','fr','ge','de','gr','hu','is',
    'ie','it','xk','lv','lt','lu','mt','md','me','nl','mk','no','pl','pt','ro','ru','rs','sk','si','es','se','ch','tr','ua','gb',
    'ai','ag','ar','bs','bb','bz','bm','bo','br','vg','ky','cl','co','cr','dm','do','ec','sv','gd','gt','gy','hn','jm','mx','ms','ni','pa','py','pe','kn','lc','vc','sr','tt','tc','uy','ve','ca','us'
]
# Output files
VALID_FILE = "valid_ids.csv"
INVALID_FILE = "invalid_ids.txt"

# === Load newly scraped IDs from TXT ===
def load_new_ids(existing_csv):
    new_ids = set()
    try:
        with open(existing_csv, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    new_ids.add(line)
        print(f"🆕 Loaded {len(new_ids)} scraped IDs from {existing_csv}")
    except FileNotFoundError:
        print(f"⚠️ File not found: {existing_csv}, treating as empty")
    return new_ids

# === Save only unique IDs ===
def save_unique_ids(unique_ids, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for uid in sorted(unique_ids):
            f.write(uid + "\n")
    print(f"✅ Saved {len(unique_ids)} new unique IDs to {filename}")

# Generate PodcastIndex headers
def get_pi_headers():
    auth_time = str(int(time.time()))
    auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()
    return {
        "User-Agent": "MillionPodcastCrawler/1.0",
        "X-Auth-Key": API_KEY,
        "X-Auth-Date": auth_time,
        "Authorization": auth_hash
    }

def check_apple_store(itunes_id, timeout=5, sleep_time=0.5):
    """
    Check if the podcast exists in any Apple country store
    """
    base_url = "https://podcasts.apple.com/{country}/podcast/id{pid}"
    for country in COUNTRY_CODES:
        url = base_url.format(country=country, pid=itunes_id)
        try:
            r = requests.head(url, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(sleep_time)  # avoid hitting too hard
    return False

def check_apple_lookup(itunes_id):
    """
    Use the Apple Lookup API to check podcast existence
    """
    url = f"https://itunes.apple.com/lookup?id={itunes_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("resultCount", 0) > 0:
                return True
    except requests.RequestException:
        pass
    return False

def check_podcastindex(itunes_id):
    """
    Check with PodcastIndex API
    """
    url = f"https://api.podcastindex.org/api/1.0/add/byitunesid?id={itunes_id}"
    try:
        r = requests.post(url, headers=get_pi_headers(), timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") is True or data.get("feedId"):
                return True
    except requests.RequestException:
        pass
    return False

def validate_ids(ids):
    valid_ids = set()
    invalid_ids = set()

    with open(VALID_FILE, "w", newline="") as csvfile, open(INVALID_FILE, "w") as invalidfile:
        writer = csv.writer(csvfile)
        writer.writerow(["itunesId"])

        for pid in ids:
            print(f"🔍 Checking {pid}...")
            is_valid = False

            # Step 1: Apple Store (country-specific)
            if check_apple_store(pid):
                is_valid = True
                print(f"✅ {pid} valid in Apple Store")

            # Step 2: Apple Lookup API
            elif check_apple_lookup(pid):
                is_valid = True
                print(f"✅ {pid} valid via Apple Lookup API")

            # Step 3: PodcastIndex API
            elif check_podcastindex(pid):
                is_valid = True
                print(f"✅ {pid} valid via PodcastIndex API")

            # Final decision
            if is_valid:
                valid_ids.add(pid)
                writer.writerow([pid])
            else:
                invalid_ids.add(pid)
                invalidfile.write(f"{pid}\n")
                print(f"❌ {pid} invalid everywhere")

    return valid_ids, invalid_ids


def get_gz_links_from_index(xml_url):
    try:
        print(f"📥 Fetching sitemap index: {xml_url}")
        r = requests.get(xml_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "xml")
        gz_links = [loc.text for loc in soup.find_all("loc") if loc.text.endswith(".gz")]
        print(f"📄 Found {len(gz_links)} .gz files")
        return gz_links
    except Exception as e:
        print(f"❌ Error fetching sitemap index: {e}")
        return []

# === Extract podcast IDs directly from .gz file contents ===
def extract_ids_from_gz(gz_url):
    ids = set()
    try:
        print(f"➡️ Downloading .gz: {gz_url}")
        r = requests.get(gz_url, timeout=15)
        r.raise_for_status()
        with gzip.open(io.BytesIO(r.content), "rt", encoding="utf-8") as f:
            content = f.read()
            found = re.findall(r'/id(\d{8,})', content)
            ids.update(found)
        print(f"   🎯 Found {len(ids)} IDs in this file")
    except Exception as e:
        print(f"❌ Error processing {gz_url}: {e}")
    return ids

# === Save IDs to file ===
def save_ids_to_file(ids, filename="new.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for pid in sorted(ids):
            f.write(f"{pid}\n")
    print(f"✅ Saved {len(ids)} unique IDs to {filename}")

existing_csv = "../apple_ids.csv"     # CSV with old IDs
new_ids_file = "new.txt"              # TXT with newly scraped IDs
output_file = "new_unique_ids.txt"    # Output: only IDs not in CSV

# === Load existing IDs from CSV ===
def load_existing_ids(csv_path):
    existing = set()
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    existing.add(row[0].strip())
        print(f"📂 Loaded {len(existing)} IDs from {csv_path}")
    except FileNotFoundError:
        print(f"⚠️ File not found: {csv_path}, treating as empty")
    return existing

# === Load new scraped IDs from TXT ===
def load_new_ids(txt_path):
    new_ids = set()
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    new_ids.add(line)
        print(f"🆕 Loaded {len(new_ids)} scraped IDs from {txt_path}")
    except FileNotFoundError:
        print(f"⚠️ File not found: {txt_path}, treating as empty")
    return new_ids

# === Save unique IDs to a file ===
def save_unique_ids(unique_ids, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for uid in sorted(unique_ids):
            f.write(uid + "\n")
    print(f"✅ Saved {len(unique_ids)} new unique IDs to {filename}")

# === Main ===
def main():
    existing_ids = load_existing_ids(existing_csv)

    # 2. Crawl sitemap and collect all new IDs
    index_url = "https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml"
    all_ids = set()
    gz_links = get_gz_links_from_index(index_url)
    for gz_url in gz_links:
        ids = extract_ids_from_gz(gz_url)
        all_ids.update(ids)
    print(f"\n🎧 Total IDs found in sitemaps: {len(all_ids)}")

    # 3. Keep only IDs not in existing CSV
    unique_ids = all_ids - existing_ids
    print(f"✨ Found {len(unique_ids)} new IDs not in CSV")

    # 4. Save these new unique IDs
    save_ids_to_file(unique_ids, output_file)

    # 5. Optionally validate them
    validate_ids(unique_ids)

if __name__ == "__main__":
    main()


# # Prepare API headers
# auth_time = str(int(time.time()))
# auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()
# headers = {
#     "User-Agent": "MillionPodcastCrawler/1.0",
#     "X-Auth-Key": API_KEY,
#     "X-Auth-Date": auth_time,
#     "Authorization": auth_hash
# }

# # === File paths ===
# existing_csv = "../apple_ids.csv"     # The old/existing IDs you already have
# new_ids_file = "new.txt"              # IDs you just scraped in your main script
# output_file = "new_unique_ids.txt"    # Output: only IDs that are new

# # === Load existing IDs from CSV ===
# def load_existing_ids(csv_path):
#     existing = set()
#     try:
#         with open(csv_path, "r", encoding="utf-8") as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 if row:  # ignore blank rows
#                     existing.add(row[0].strip())
#         print(f"📂 Loaded {len(existing)} IDs from {csv_path}")
#     except FileNotFoundError:
#         print(f"⚠️ File not found: {csv_path}, treating as empty")
#     return existing

# # === Load newly scraped IDs from TXT ===
# def load_new_ids(txt_path):
#     new_ids = set()
#     try:
#         with open(txt_path, "r", encoding="utf-8") as f:
#             for line in f:
#                 line = line.strip()
#                 if line:
#                     new_ids.add(line)
#         print(f"🆕 Loaded {len(new_ids)} scraped IDs from {txt_path}")
#     except FileNotFoundError:
#         print(f"⚠️ File not found: {txt_path}, treating as empty")
#     return new_ids

# # === Save only unique IDs ===
# def save_unique_ids(unique_ids, filename):
#     with open(filename, "w", encoding="utf-8") as f:
#         for uid in sorted(unique_ids):
#             f.write(uid + "\n")
#     print(f"✅ Saved {len(unique_ids)} new unique IDs to {filename}")

# # to validate ids
# def validate_ids(ids, valid_csv="valid_ids.csv", invalid_txt="invalid_ids.txt", timeout=5):

#     valid_ids = set()
#     invalid_ids = set()
#     base_url = "https://podcasts.apple.com/{country}/podcast/id{id}"

#     # open CSV for valid IDs
#     with open(valid_csv, "w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["id"])  # header row

#         for pid in ids:
#             is_valid = False
#             for country in COUNTRY_CODES:
#                 url = base_url.format(country=country, id=pid)
#                 try:
#                     r = requests.head(url, timeout=timeout, allow_redirects=True)
#                     if r.status_code == 200:
#                         valid_ids.add(pid)
#                         writer.writerow([pid])   # save once
#                         is_valid = True
#                         print(f"✅ {pid} valid (found in {country})")
#                         break   # no need to check more countries for this ID
#                 except requests.RequestException:
#                     continue

#             if not is_valid:
#                 invalid_ids.add(pid)
#                 print(f"❌ {pid} invalid in all countries")

#     # save invalid IDs to txt
#     with open(invalid_txt, "w", encoding="utf-8") as f:
#         for pid in sorted(invalid_ids):
#             f.write(pid + "\n")

#     print(f"\n📂 Saved {len(valid_ids)} valid IDs to {valid_csv}")
#     print(f"📂 Saved {len(invalid_ids)} invalid IDs to {invalid_txt}")

#     return valid_ids, invalid_ids


# # === Main ===
# def main():
#     existing_ids = load_existing_ids(existing_csv)
#     new_ids = load_new_ids(new_ids_file)

#     unique_ids = new_ids - existing_ids
#     print(f"✨ Found {len(unique_ids)} new IDs not in {existing_csv}")
#     validate_ids(unique_ids)
#     save_unique_ids(unique_ids, output_file)

# if __name__ == "__main__":
#     main()
