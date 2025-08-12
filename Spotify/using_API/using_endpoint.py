# Collecting data from all possible country wise endpoints for top podcasts
from collections import defaultdict
import requests
import csv
import time

# List of ISO 3166-1 alpha-2 country codes
Three = [
    # Has three categories only - top podcasts, trending podcasts, top episodes
    "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id", "ie", "it", "jp","nz","no","ph","es", "nl"]

    # Has all categories - 17
Seventeen = [  "au", "us","gb", "br", "de", "mx", "se"]
One =[ 
    # only top podcasts available
    "al", "ad", "ae", "az", "ba", "be", "bg", "bh",
    "bo", "br", "bw", "ch", "cr", "cy", "cz", "do", 
    "dz", "ec", "ee", "eg", "es", "fi", "fr", "gb", 
    "ge", "gh", "gr", "gt",  "hk", "hn", "hr", "hu", 
    "id", "ie", "il", "in", "is", "jm", "jo", "jp", 
    "ke", "kh", "kr", "kw", "lb", "lt", "lu", "lv", 
    "ma", "mk", "mt", "mu" , # 54
    "mw", "mx", "my", "mz", "na", "ng", "ni",  "np",  
    "om", "pa", "pe", "ph", "pl", "pt", "py","qa", 
    "ro", "rs", "rw" , # 62
    "sa", "se", "sg", "si", "sk", "sn", "sv", "th", 
    "tn", "tr", "tt", "tw", "tz", "ua", "uy", "uz", 
    "vn", "za", "zm", "zw"]
     # low number of podcasts
    #   "lc", # 3
    #   "mc", # 11
    #   "mg", # 46 
    #   "me", # 35
    #   "bb", # 22
    #   "bs", # 33
    #   "bz", # 14
    #   "fj", # 12
    #   "gm", # 12
    #   "gy", # 15
    #   "mn", # 43
    #   "ne", # 6
    #   "mo", # 28
    #   "pg", # 25
    #   "ps", # 42
    #   "sc", # 3
    #   "sl", # 22
    #   "sm", # 3
    #   "sr", # 6
    #   "sz", # 14
 
failed_requests = []
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
    

def save_to_csv(all_rows, filename="spotify_podcast_top_charts.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Rank", "Name", "ChartRankMove", "ShowID"])
        writer.writerows(all_rows)

unique_show_ids = set()
def main():
    all_rows = []
    region_counts = defaultdict(int)
    for country in sorted(set(One + Three + Seventeen)):
        print(f"[INFO] Fetching region: {country}")
        items = fetch_charts(country)
        if not items:
            print(f"[ERROR] Failed for region {country}")
            failed_requests.append((country))
            continue

        region_counts[country] = len(items)
        # enumerate will give position-based rank
        for idx, item in enumerate(items, start=1):
            name = item.get("showName", "")
            move = item.get("chartRankMove", "")
            show_uri = item.get("showUri", "")
            show_id = show_uri.split(":")[-1] if show_uri else ""
            all_rows.append([country, idx, name, move, show_id])

            if show_id:
                unique_show_ids.add(show_id)
        
        if failed_requests:
            print(f"\n[INFO] Retrying {len(failed_requests)} failed requests...\n")
    
    retry_failed = []
    
    for country, category in failed_requests:
        items = fetch_charts(country, category)
        if not items:
            print(f"[ERROR] Retry failed for {country.upper()} - {category}")
            retry_failed.append((country, category))
            continue

        for idx, item in enumerate(items, start=1):
            show_uri = item.get("showUri", "")
            show_id = show_uri.split(":")[-1] if show_uri else ""

            all_rows.append([
                country,
                category,
                idx,
                item.get("showName", ""),
                item.get("showPublisher", ""),
                item.get("showImageUrl", ""),
                item.get("showDescription", ""),
                item.get("chartRankMove", ""),
                show_id
            ])

            if show_id:
                unique_show_ids.add(show_id)

        time.sleep(0.5)

    if retry_failed:
        print(f"\n[ERROR] These requests failed even after retry:")
        for country in retry_failed:
            print(f"  - {country.upper()}")


    save_to_csv(all_rows)

    print(f"[DONE] Saved {len(all_rows)} rows to spotify_podcast_top_charts.csv\n")
    print(f"Unique ids {len(unique_show_ids)}")
       
        # Print per-region counts
    print("\n[SUMMARY] Podcasts per region:")
    for region, count in sorted(region_counts.items()):
        print(f"{region.upper()}: {count}")

if __name__ == "__main__":
    main()
