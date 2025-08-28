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

#--------------------------------------
# 5. Validate IDs
# --------------------------------------
def get_pi_headers():
    auth_time = str(int(time.time()))
    auth_hash = hashlib.sha1((API_KEY + API_SECRET + auth_time).encode("utf-8")).hexdigest()
    return {
        "User-Agent": "MillionPodcastCrawler/1.0",
        "X-Auth-Key": API_KEY,
        "X-Auth-Date": auth_time,
        "Authorization": auth_hash
    }

def check_apple_lookup(itunes_id):
    url = f"https://itunes.apple.com/lookup?id={itunes_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("resultCount", 0) > 0
    except requests.RequestException:
        pass
    time.sleep(1)
    return False

def check_podcastindex(itunes_id):
    url = f"https://api.podcastindex.org/api/1.0/add/byitunesid?id={itunes_id}"
    try:
        r = requests.post(url, headers=get_pi_headers(), timeout=5)
        if r.status_code == 200:
            data = r.json()
            return bool(data.get("status") or data.get("feedId"))
    except requests.RequestException:
        pass
    return False

def check_apple_store(itunes_id, timeout=5, sleep_time=1):
    base_url = "https://podcasts.apple.com/{country}/podcast/id{pid}"
    for country in COUNTRY_CODES:
        url = base_url.format(country=country, pid=itunes_id)
        try:
            r = requests.head(url, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(sleep_time)
    return False

def validate_ids(ids, valid_file="valid_ids.txt", invalid_file="invalid_ids.txt"):
    valid, invalid = set(), set()

    with open(valid_file, "w", encoding="utf-8") as vf, open(invalid_file, "w", encoding="utf-8") as inf:
        for pid in ids:
            print(f"🔍 Checking {pid}...")
            if check_apple_lookup(pid) or check_podcastindex(pid) or check_apple_store(pid):
                valid.add(pid)
                vf.write(pid + "\n")
                print(f"✅ {pid} VALID")
            else:
                invalid.add(pid)
                inf.write(pid + "\n")
                print(f"❌ {pid} INVALID")

    print(f"\n📂 {len(valid)} valid IDs saved to {valid_file}")
    print(f"📂 {len(invalid)} invalid IDs saved to {invalid_file}")
    return valid, invalid


# --------------------------------------
# Example usage
# --------------------------------------
if __name__ == "__main__":
    ids = set()
    with open("different_20250827_183606.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                ids.add(line)
    
    validate_ids(ids)