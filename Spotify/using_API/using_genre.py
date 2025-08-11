
from playwright.sync_api import sync_playwright
import re
import requests
import base64
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import password 

CLIENT_ID = password.CLIENT_ID
CLIENT_SECRET = password.CLIENT_SECRET


# Encode credentials for token
auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

# Get access token
def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}
    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

# Spotify-supported markets
MARKETS = [
    "AD","AE","AG","AL","AM","AO","AR","AT","AU","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BN","BO","BR","BS","BT","BW","BY","BZ",
    "CA","CD","CG","CH","CI","CL","CM","CO","CR","CV","CW","CY","CZ","DE","DJ","DK","DM","DO","DZ",
    "EC","EE","EG","ES","ET","FI","FJ","FM","FR","GA","GB","GD","GE","GH","GM","GN","GQ","GR","GT","GW","GY",
    "HK","HN","HR","HT","HU","ID","IE","IL","IN","IQ","IS","IT",
    "JM","JO","JP","KE","KG","KH","KI","KM","KN","KR","KW","KZ",
    "LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY",
    "MA","MC","MD","ME","MG","MH","MK","ML","MN","MO","MR","MT","MU","MV","MW","MX","MY","MZ",
    "NA","NE","NG","NI","NL","NO","NP","NR","NZ","OM",
    "PA","PE","PG","PH","PK","PL","PS","PT","PW","PY",
    "QA","RO","RS","RW","SA","SB","SC","SE","SG","SI","SK","SL","SM","SN","SR","ST","SV","SZ",
    "TD","TG","TH","TJ","TL","TN","TO","TR","TT","TV","TZ",
    "UA","UG","US","UY","UZ","VC","VE","VN","VU","WS","ZA","ZM","ZW"
]
GENRE_URL = "https://open.spotify.com/genre/0JQ5DAqbMKFEKYLBUxreJF"

def scrape_genre_for_market(page, market_code):
    shows = set()
    
    # Spotify doesn’t allow /us/ in the middle, so we use ?country= param
    url = f"{GENRE_URL}?country={market_code}"
    print(f"[{market_code}] Visiting: {url}")
    page.goto(url, timeout=60000)
    
    # Wait for page to load
    page.wait_for_selector("a[href*='/show/']", timeout=30000)
    
    # Scroll until no more new content
    last_height = 0
    while True:
        page.mouse.wheel(0, 4000)
        time.sleep(1)
        height = page.evaluate("document.body.scrollHeight")
        if height == last_height:
            break
        last_height = height
    
    # Extract show IDs
    links = page.query_selector_all("a[href*='/show/']")
    for link in links:
        href = link.get_attribute("href")
        match = re.search(r"/show/([A-Za-z0-9]+)", href)
        if match:
            shows.add(match.group(1))
    
    print(f"[{market_code}] Found {len(shows)} shows")
    return shows

def main():
    all_shows = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for market in MARKETS:
            try:
                shows = scrape_genre_for_market(page, market)
                all_shows.update(shows)
            except Exception as e:
                print(f"[{market}] Error: {e}")
        
        browser.close()
    
    print("="*50)
    print(f"TOTAL unique podcasts: {len(all_shows)}")
    with open("spotify_podcast_ids.txt", "w") as f:
        for show_id in all_shows:
            f.write(show_id + "\n")

if __name__ == "__main__":
    main()

# # Example genre/category ID — replace with correct one
# GENRE_ID = "0JQ5DAqbMKFD0Jc9BXRvme"

# def get_podcasts_for_market(market, token):
#     # Example: This uses playlists for a category, replace with actual API mapping for genre
#     url = f"https://api.spotify.com/v1/browse/categories/{GENRE_ID}/playlists?market={market}&limit=10"
#     headers = {"Authorization": f"Bearer {token}"}
#     r = requests.get(url, headers=headers)
#     if r.status_code == 200:
#         return r.json()
#     else:
#         print(f"Failed for {market}: {r.status_code}")
#         return None

# # Main run
# token = get_access_token()
# results = {}

# for m in markets:
#     print(f"Fetching for market: {m}")
#     data = get_podcasts_for_market(m, token)
#     if data:
#         results[m] = data
#     time.sleep(0.2)  # avoid hitting rate limits

# # Example output
# for market, data in results.items():
#     print(market, "=>", [p
#                          ["name"] for p in data.get("playlists", {}).get("items", [])])
