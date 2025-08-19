from collections import defaultdict
import requests
import csv
import time

# List of ISO 3166-1 alpha-2 country codes
# Has three categories only - top podcasts, trending podcasts, top episodes
Three = [
    "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", 
    "id", "ie", "it", "jp","nz","no","ph","es", "nl", "pl"
    ]

# Has all categories - 17
Seventeen = [  
"au", "us","gb", "br", "de", "mx", "se"
]

# only top podcasts available
One =[ 
    "al", "ad", "ae", "az", "ba", "be", "bg", "bh",
    "bo", "br", "bw", "ch", "cr", "cy", "cz", "do", 
    "dz", "ec", "ee", "eg", "es",
    "ge", "gh", "gr", "gt",  "hk", "hn", "hr", "hu", 
    "id", "ie", "il", "in", "is", "jm", "jo", "jp", 
    "ke", "kh", "kr", "kw", "lb", "lt", "lu", "lv", 
    "ma", "mk", "mt", "mu" # 54, 
    "mw", "mx", "my", "mz", "na", "ng", "ni",  "np",  
    "om", "pa", "pe", "ph",  "pt", "py","qa", 
    "ro", "rs", "rw" # 62, 
    "sa", "se", "sg", "si", "sk", "sn", "sv", "th", 
    "tn", "tr", "tt", "tw", "tz", "ua", "uy", "uz", 
    "vn", "za", "zm", "zw"
]

# Categories
CATEGORIES_20 = [
    "top", "trending", "top_episodes", "arts", "business", "comedy", "education", "fiction", "history", 
    "health%252520%2526%252520fitness", "leisure", "music", "news", "religion%252520%2526%252520spirituality", 
    "science", "society%252520%2526%252520culture", "sports", "technology", "true%252520crime", "tv%252520%2526%252520film"
]

CATEGORIES_3 = ["top", "trending", "top_episodes"]

#CATEGORIES_1 = ["top"]

#COUNTRIES = sorted(set(Three + Seventeen + One))

def fetch_charts(country, category):
    """Fetch podcast chart data for a given country and category."""
    url = f"https://podcastcharts.byspotify.com/api/charts/{category}?region={country}"
    print(f"[INFO] Fetching {country.upper()} - {category} → {url}")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        items = r.json()
        if isinstance(items, dict):
            items = items.get("items", [])
        if not isinstance(items, list):
            return []
        return items
    except Exception as e:
        print(f"[ERROR] Failed for {country.upper()} - {category}: {e}")
        return []

def save_to_csv(rows, filename="spotify_podcast_charts_by_website.csv"):
    """Save results to CSV."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Category", "Rank", "ShowName", "Publisher", "ImageURL", "Description", "ChartRankMove", "ShowID"])
        writer.writerows(rows)

def main():
    all_rows = []
    unique_show_ids = set()
    region_category_counts = defaultdict(int)

    failed_requests = []
    
    # Combine all countries and process in sorted order
    for country in sorted(set( Three + Seventeen)):
        if country in Seventeen:
            categories = CATEGORIES_20
       
        else:  # falls into One
            categories = CATEGORIES_3

        for category in categories:
            items = fetch_charts(country, category)
            if not items:
                print(f"[ERROR] Failed or empty data for {country.upper()} - {category}")
                failed_requests.append((country, category))
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

            region_category_counts[(country, category)] = len(items)
            time.sleep(0.5)  # avoid hammering the server

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

        region_category_counts[(country, category)] = region_category_counts.get((country, category), 0) + len(items)
        time.sleep(0.5)

    if retry_failed:
        print(f"\n[ERROR] These requests failed even after retry:")
        for country, category in retry_failed:
            print(f"  - {country.upper()} - {category}")


    save_to_csv(all_rows)

    print(f"\n[DONE] Saved {len(all_rows)} rows to spotify_podcast_charts_by_website.csv")
    print(f"[SUMMARY] Total entries: {len(all_rows)}")
    print(f"[SUMMARY] Unique shows: {len(unique_show_ids)}")

    print("\n[SUMMARY] Podcasts per region-category:")
    for (region, category), count in sorted(region_category_counts.items()):
        print(f"{region.upper()} - {category}: {count}")

if __name__ == "__main__":
    main()

# For All categories and countries present
# [DONE] Saved 34388 rows to spotify_podcast_charts_by_category.csv
# [SUMMARY] Total entries: 34388
# [SUMMARY] Unique shows: 12558


# For only countries in the podcastcharts.byspotify.com
# [DONE] Saved 20950 rows to spotify_podcast_charts_by_website.csv
# [SUMMARY] Total entries: 20950
# [SUMMARY] Unique shows: 7877


# For all countries top page 
# [DONE] Saved 18913 rows to spotify_podcast_top_charts.csv
# Unique ids 8745



# For countries with only top page
