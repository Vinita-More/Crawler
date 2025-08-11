# Collecting data from all possible country wise endpoints for top podcasts
from collections import defaultdict
import requests
import csv
import time

# List of ISO 3166-1 alpha-2 country codes
COUNTRIES = [
    # Has three categories only - top podcasts, trending podcasts, top episodes
    "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id", "ie", "it", "jp","nz","no","ph","po","es", "nl"

    # Has all categories - 17
    "au", "us","gb", "br", "de", "mx", "se"
    
    # only top podcasts available
    "al",  "ad",  "ae","az","ba", "bb",
    
    
    # countries not present in the https://podcastcharts.byspotify.com/ but show some result - check if it shows atleast the three categories
      "be", "bg", "bh",
    "bo", "br", "bs", "bw", "bz",  "ch", "cr", "cy", "cz",
    "do", "dz", "ec", "ee", "eg", "es", "fi", "fj", "fr", "gb", "ge", "gh", "gm", 
    "gr", "gt", "gy", "hk", "hn", "hr", "hu", "id", "ie", "il", "in", "is", "it", 
    "jm", "jo", "jp", "ke", "kh", "kr", "kw", "kz", "lb", "lc", "lt", "lu", "lv", 
    "ma", "mc", "md", "me", "mg", "mk", "mn", 
    "mo", "mt", "mu", "mw", "mx", "my", "mz", "na", "ne", "ng", "ni",  "np",  "om", "pa", "pe", "pg", "ph", "pl", "ps", "pt", "py",
    "qa", "ro", "rs", "rw", "sa", "sc", "se", "sg", "si", "sk", "sl", "sm", "sn",
    "sr", "sv", "sz", "th", "tn", "tr", "tt", "tw", "tz", "ua", 
     "uy", "uz", "vn", "za", "zm", "zw"
     
 ]

def fetch_charts(region_code):
    url = f"https://podcastcharts.byspotify.com/api/charts/top?region={region_code}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Handle list or dict
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("items", [])
        else:
            return []
    except Exception as e:
        print(f"[ERROR] Failed for region {region_code}: {e}")
        return None

def save_to_csv(all_rows, filename="spotify_podcast_charts.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Rank", "Name", "ChartRankMove", "ShowID"])
        writer.writerows(all_rows)


def main():
    all_rows = []
    region_counts = defaultdict(int)
    for country in COUNTRIES:
        print(f"[INFO] Fetching region: {country}")
        items = fetch_charts(country)
        if not items:
            continue

        region_counts[country] = len(items)
        # enumerate will give position-based rank
        for idx, item in enumerate(items, start=1):
            name = item.get("showName", "")
            move = item.get("chartRankMove", "")
            show_uri = item.get("showUri", "")
            show_id = show_uri.split(":")[-1] if show_uri else ""
            all_rows.append([country, idx, name, move, show_id])

        time.sleep(1)  # avoid hammering the server

    save_to_csv(all_rows)
    print(f"[DONE] Saved {len(all_rows)} rows to spotify_podcast_charts.csv")

        # Print per-region counts
    print("\n[SUMMARY] Podcasts per region:")
    for region, count in sorted(region_counts.items()):
        print(f"{region.upper()}: {count}")

if __name__ == "__main__":
    main()
