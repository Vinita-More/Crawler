import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import os

genre_ids = [
    1301, 1302, 1303, 1304, 1305, 1306, 1309, 1310, 1314, 1318, 1320, 1321,
    1324, 1545, 1483, 1488, 1502, 1487, 1498, 1512, 1544, 1500, 1533, 1543, 
    1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1546, 1547, 1548, 
    1550, 1551, 1552, 1553, 1554, 1555, 1556, 1557, 1558, 1559, 1560, 1561, 
    1562, 1563, 1564, 1565, 1533, 1517, 1489, 1482, 1493, 1549, 1541, 
]

country_codes = ["us", "de", "ca", "ph", "pt", "ro", "sk", "th", "ua", "ve", "vn", "az"] 

CSV_FILENAME = "../apple_ids.csv"
NEW_FILENAME = "new_ids.txt"

# Load existing podcast IDs from CSV
def load_existing_ids(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        return {row[0] for row in reader if row}
    
# Generate links
def generate_apple_podcast_links(genre_ids, country_codes):
    base_url = "https://podcasts.apple.com/{country}/genre/id{genre_id}"
    links = []
    for country in country_codes:
        for genre_id in genre_ids:
            links.append(base_url.format(country=country, genre_id=genre_id))
    return links

def extract_podcast_ids_from_page(url):
    print(f"Fetching: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ApplePodcastScraper/1.0)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    podcast_ids = []

    main_tag = soup.find("main")
    if not main_tag:
        print("No <main> tag found.")
        return []

    # Find all <a> tags within <main> and extract hrefs
    for a_tag in main_tag.find_all("a", href=True):
        href = a_tag["href"]
        match = re.search(r'/id(\d+)', href)
        if match:
            podcast_ids.append(match.group(1))

    return podcast_ids


TXT_FILENAME = "pid.txt"
# Save to pid.txt
def save_ids_to_txt(ids, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for pid in sorted(ids):
            f.write(f"{pid}\n")
    print(f"✅ Saved {len(ids)} IDs to {filename}")

# Load existing IDs from CSV
def load_existing_ids_from_csv(filename):
    if not os.path.exists(filename):
        print("⚠️ CSV file not found.")
        return set()
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        return {row[0] for row in reader if row}

# Compare two ID sets
def compare_ids(new_ids, existing_ids):
    new_only = new_ids - existing_ids
    common = new_ids & existing_ids
    return new_only, common


# MAIN
if __name__ == "__main__":
    links = generate_apple_podcast_links(genre_ids, country_codes)

    all_ids = set()

    for link in links:
        ids = extract_podcast_ids_from_page(link)
        print(f"Found {len(ids)} podcast IDs")
        all_ids.update(ids)
        time.sleep(1)  # Be polite and avoid being blocked

    print(f"\n🔢 Total unique podcast IDs collected: {len(all_ids)}")
    save_ids_to_txt(all_ids, TXT_FILENAME)

    # Comparison with CSV
    existing_ids = load_existing_ids_from_csv(CSV_FILENAME)
    new_only, common = compare_ids(all_ids, existing_ids)

    print(f"🆕 New IDs (not in CSV): {len(new_only)}")
    print(f"✅ Already in CSV: {len(common)}")
    save_ids_to_txt(new_only, NEW_FILENAME)

# Extract podcast IDs from each genre page
# def extract_podcast_ids_from_page(url):
#     print(f"Fetching: {url}")
#     headers = {
#         "User-Agent": "Mozilla/5.0 (compatible; ApplePodcastScraper/1.0)"
#     }

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()
#     except requests.RequestException as e:
#         print(f"Error fetching {url}: {e}")
#         return []

#     soup = BeautifulSoup(response.text, "lxml")

#     podcast_ids = []

#     # Find the section with data-testid="shelf-body"
#     shelf_body = soup.find("div", {"data-testid": "shelf-body"})
#     if not shelf_body:
#         return []

#     for a_tag in shelf_body.select("a.editorial-card__link"):
#         href = a_tag.get("href", "")
#         match = re.search(r'/id(\d+)', href)
#         if match:
#             podcast_ids.append(match.group(1))

#     return podcast_ids

# genre_ids = [
#     1301,  # Arts
#     1302,  # Business
#     1303,  # Comedy
#     1304,  # Education
#     1305,  # Kids & Family
#     1306, #Food
#     1309,  # TV & Film
#     1310,  # Music
#     1314,  # Religion & Spirituality
#     1318,  # Technology
#     1320,  # Places and Travel
#     1321,  # Business
#     1324,  # Society and culture
#     1545,  #sports
#     1488,  # True Crime
#     1502,  # Leisure
#     1482, #books
#     1487, #history
#     1489, # news
#     1483, # fiction
#     1493, #Entrepreneurship
#     1498, #Language learning
#     1512, #Health and fitness
#     1517, # mental health
#     1544, #Relationships
#     1500, #Self improvement
#     1533, #science
#     1543, #Documentry
#     1503, # Automotive
#     1504, #Aviation 
#     1505, #hobbies
#     1506, #Crafts
#     1507, #Games
#     1508, #Homes and Garden
#     1509, #Video games
#     1510, #Animation and Manga
#     1511, #Government
#     1533, #science
#     1541, # life sciences
#     1542, # physics
#     1546,#Soccer
#     1547, #football
#     1548, #basketball
#     1549, #baseball
#     1550, #hockey
#     1551, # Running
#     1552,#rugby
#     1553, #golf
#     1554, # cricket
#     1555, # wrestling
#     1556, # tennis
#     1557, # volleyball
#     1558, # swimming
#     1559, # wilderness
#     1560, # Fantasy Sports
#     1561, #tv reviews 
#     1562, # after shows
#     1563, # film reviews
#     1564, # film history
#     1565, # film interviews


# ]
# country_codes = [
#     "us", "gb", "ca", "au", "in", "de", "fr", "jp", "kr", "br", "mx", "cn", "it", "es",
#     "ru", "nl", "se", "no", "fi", "dk", "ie", "nz", "za", "sg", "hk", "tw", "be", "ch",
#     "at", "pl", "tr", "sa", "ae", "ar", "cl", "co", "cz", "gr", "hu", "id", "il", "my",
#     "ph", "pt", "ro", "sk", "th", "ua", "ve", "vn", "az"
# ]

# country_codes = [
#     ae, ag, ai, al, am, ao, ar, at, au, az,
# bb, be, bf, bg, bh, bj, bm, bn, bo, br,
# bs, bt, bw, by, bz, ca, cg, ch, cl, cn,
# co, cr, cy, cz, de, dk, dm, do, dz, ec,
# ee, eg, es, fi, fr, gb, gd, gh, gm, gr,
# gt, gw, gy, hk, hn, hr, hu, id, ie, il,
# in, is, it, jm, jo, jp, ke, kg, kh, kn,
# kr, kw, ky, kz, la, lb, lc, lk, lr, lt,
# lu, lv, md, mg, mk, ml, mn, mo, mr, ms,
# mt, mu, mw, mx, my, ne, ng, ni, nl, no,
# np, om, pa, pe, ph, pk, pl, pt, py, qa,
# ro, ru, sa, sb, sc, se, sg, sk, si, sl,
# sn, sr, st, sv, sz, td, tg, th, tj, tm,
# tn, tr, tt, tw, tz, ua, ug, us, uy, uz,
# vc, ve, vg, vn, ye, za, zw
# ]
# #Generating links
# def generate_apple_podcast_links(genre_ids, country_codes):
#     base_url = "https://podcasts.apple.com/{country}/genre/{genre_id}"
#     links = []

#     for country in country_codes:
#         for genre_id in genre_ids:
#             url = base_url.format(country=country, genre_id=genre_id)
#             links.append(url)
    
#     return links

# links = generate_apple_podcast_links(genre_ids, country_codes)
