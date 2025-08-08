import requests
from bs4 import BeautifulSoup
import re
import time

countries = [
'dz', 'ao', 'am', 'az', 'bh', 'bj', 'bw', 'bn', 'bf', 'cm', 'cv', 'td', 'ci', 'cd', 'eg',
'sz', 'ga', 'gm', 'gh', 'gw', 'in', 'iq', 'il', 'jo', 'ke', 'kw', 'lb', 'lr', 'ly', 'mg',
'mw', 'ml', 'mr', 'mu', 'ma', 'mz','na', 'ne', 'ng', 'om', 'qa', 'cg', 'rw', 'sa', 'sn',
'sc', 'sl', 'za', 'lk', 'tj', 'tz', 'tn', 'tm', 'ae', 'ug', 'ye', 'zm','zw', 'au', 'bt', 
'kh', 'cn', 'fj', 'hk', 'id', 'jp', 'kz', 'kr', 'kg', 'la', 'mo', 'my', 'mv', 'fm','mn',
'mm', 'np', 'nz', 'pg', 'ph', 'sg', 'sb', 'tw', 'th', 'to', 'uz', 'vu', 'vn', 'at', 'by',
'be', 'ba', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'fr', 'ge', 'de', 'gr', 'hu', 'is',
'ie', 'it', 'xk', 'lv', 'lt', 'lu', 'mt', 'md', 'me', 'nl', 'mk', 'no', 'pl', 'pt', 'ro',
'ru', 'rs', 'sk', 'si', 'es', 'se', 'ch', 'tr', 'ua', 'gb', 'ai', 'ag', 'ar', 'bs', 'bb',
'bz', 'bm', 'bo', 'br', 'vg', 'ky', 'cl', 'co', 'cr', 'dm', 'do', 'ec', 'sv', 'gd', 'gt',
'gy', 'hn', 'jm', 'mx', 'ms', 'ni', 'pa', 'py', 'pe', 'kn', 'lc', 'vc', 'sr', 'tt', 'tc',
'uy', 've','ca', 'us'
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

all_ids = set()
falied = []
for country in countries:
    url = f"https://podcasts.apple.com/{country}/browse"
    print(f"Fetching: {url}")

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"❌ Failed for {country} - Status {r.status_code}")
            falied.append(country)
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        # Select all <a> tags with href containing /id<number>
        for a in soup.select("a[href*='/id']"):
            href = a["href"]
            match = re.search(r'/id(\d+)', href)
            if match:
                all_ids.add(match.group(1))

        print(f"✅ {country}: Found {len(all_ids)} total IDs so far")

        time.sleep(5)  

    except Exception as e:
        print(f"Error fetching {country}: {e}")

# Save to file
with open("browse_page_ids.txt", "w", encoding="utf-8") as f:
    for pid in sorted(all_ids):
        f.write(pid + "\n")

for i in falied:
    print(i)

print(f"\n🎯 Done! Found {len(all_ids)} Apple Podcast IDs.")
