import requests
from bs4 import BeautifulSoup
import re

# Countries to iterate over
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

# All genres (main + sub)
categories = [
    1301, 1302, 1303, 1304, 1305, 1309, 1310, 1314, 1318, 1321, 1324,
    1482, 1483, 1487, 1488, 1489, 1493, 1498, 1500, 1502, 1511, 1512,
    1517, 1521, 1533, 1543, 1544, 1545,
    1306, 1320, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1533,
    1541, 1542, 1546, 1547, 1548, 1549, 1550, 1551, 1552, 1553, 1554,
    1555, 1556, 1557, 1558, 1559, 1560, 1561, 1562, 1563, 1564, 1565
]

base_url = "https://podcasts.apple.com/{country}/genre/{category}"
min_len = 8
max_len = 16
all_ids = set()       # master set for unique IDs
failed_logs = []      # store (country, category_id, url) for all failures

for country in countries:
    print(f"\n=== Scraping for country: {country} ===")
    
    for category_id in categories:
        url = base_url.format(country=country, category=category_id)
        print(f"Fetching: {url}")
        
        try:
            r = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }, timeout=10)

            if r.status_code != 200:
                print(f"Failed to fetch {url} (status {r.status_code})")
                failed_logs.append((country, category_id, url))
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/podcast/']"):
                href = a.get("href", "")
                match = re.search(r"/id(\d+)", href)
                if match:
                    pid = match.group(1)
                    if min_len <= len(pid) <= max_len:
                        all_ids.add(pid)

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            failed_logs.append((country, category_id, url))

print(f"\n✅ Total unique IDs collected: {len(all_ids)}")

# Save all unique IDs in one file
with open("podcast_ids.txt", "w", encoding="utf-8") as f:
    for pid in sorted(all_ids):
        f.write(f"{pid}\n")

# Save all failures in one file
if failed_logs:
    with open("failed.txt", "w", encoding="utf-8") as f:
        for country, category_id, url in failed_logs:
            f.write(f"Country: {country} | Genre: {category_id} | URL: {url}\n")
