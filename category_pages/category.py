
import requests
from bs4 import BeautifulSoup
import re

category = [
    1301, # arts
    1302,  # Personal Journals
    1303,  # Comedy
    1304,  # Education
    1305,  # Kids & Family
    1309,  # TV & Film
    1310,  # Music
    1314,  # Religion & Spirituality
    1318,  # Technology
    1321,  # Business
    1324,  # Society and culture
    1482, #books
    1483, # fiction
    1487, #history
    1488,  # True Crime
    1489, # news
    1493, #Entrepreneurship
    1498, #Language learning
    1500, #Self improvement
    1502,  # Leisure
    1511, # Government
    1512, #Health and fitness
    1517, # mental health
    1521, # parenting
    1533, #science
    1543, #Documentry
    1544, #Relationships
    1545,  #sports 
    # sub categories
    
    1306, #Food
    1320,  # Places and Travel
    1503, # Automotive
    1504, #Aviation 
    1505, #hobbies
    1506, #Crafts
    1507, #Games
    1508, #Homes and Garden
    1509, #Video games
    1510, #Animation and Manga
    1533, #science
    1541, # life sciences
    1542, # physics
    1546,#Soccer
    1547, #football
    1548, #basketball
    1549, #baseball
    1550, #hockey
    1551, # Running
    1552,#rugby
    1553, #golf
    1554, # cricket
    1555, # wrestling
    1556, # tennis
    1557, # volleyball
    1558, # swimming
    1559, # wilderness
    1560, # Fantasy Sports
    1561, #tv reviews 
    1562, # after shows
    1563, # film reviews
    1564, # film history
    1565, # film interviews
    ]


base_url = "https://podcasts.apple.com/us/genre/"
min_len = 8
max_len = 16


all_ids = set()
failed = []
for categoryid in category:
    url = f"{base_url}{categoryid}"
    print(f"Fetching: {url}")
    try:
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }, timeout=10)
        
        if r.status_code != 200:
            print(f"Failed to fetch {url} (status {r.status_code})")
            failed.append((categoryid,url))
            continue
        
        soup = BeautifulSoup(r.text, "html.parser")
      
        for a in soup.select("a[href*='/podcast/']"):
            href = a.get("href", "")
            match = re.search(r"/id(\d+)", href)
            if match:
                pid = match.group(1)
                if (min_len <= len(pid) <= max_len):
                    all_ids.add(pid)
 

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        failed.append(categoryid)
        
print("length of all ids is : ", len(all_ids))
# ===== RESULTS =====
# for ids in all_ids:
#     print(ids)



if failed:
    print("\n=== Failed Fetches ===")
    for categoryid, url in failed:
        print(f"Genre {categoryid} | URL: {url}")

# Save to new.txt
with open("new.txt", "w", encoding="utf-8") as f:
    for itunes_id in sorted(all_ids):
        f.write(f"{itunes_id}\n")





subcategories =[
    1306, #Food
    1320,  # Places and Travel
    1503, # Automotive
    1504, #Aviation 
    1505, #hobbies
    1506, #Crafts
    1507, #Games
    1508, #Homes and Garden
    1509, #Video games
    1510, #Animation and Manga
    1533, #science
    1541, # life sciences
    1542, # physics
    1546,#Soccer
    1547, #football
    1548, #basketball
    1549, #baseball
    1550, #hockey
    1551, # Running
    1552,#rugby
    1553, #golf
    1554, # cricket
    1555, # wrestling
    1556, # tennis
    1557, # volleyball
    1558, # swimming
    1559, # wilderness
    1560, # Fantasy Sports
    1561, #tv reviews 
    1562, # after shows
    1563, # film reviews
    1564, # film history
    1565, # film interviews
             ]
