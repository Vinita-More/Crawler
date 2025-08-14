# comparison without top episodes 
from collections import defaultdict
import requests
import csv
import time

# List of ISO 3166-1 alpha-2 country codes
Three = [
    "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", 
    "id", "ie", "it", "jp", "nz", "no", "ph", "es", "nl"
]

# Has all categories - 17
Seventeen = [  
    "au", "us", "gb", "br", "de", "mx", "se"
]

# Categories
CATEGORIES_20 = [
    "top", "trending", "top_episodes", "arts", "business", "comedy", "education", "fiction", "history", 
    "health%252520%2526%252520fitness", "leisure", "music", "news", "religion%252520%2526%252520spirituality", 
    "science", "society%252520%2526%252520culture", "sports", "technology", "true%252520crime", "tv%252520%2526%252520film"
]

CATEGORIES_3 = ["top", "trending", "top_episodes"]


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


def save_to_csv(rows, filename="14_08_with_top_episodes.csv"):
    """Save results to CSV."""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Region", "Category", "Rank", "ShowName", "Publisher",
            "ImageURL", "Description", "ChartRankMove", "ShowID",
            "EpisodeID", "EpisodeName"
        ])
        writer.writerows(rows)


def main():
    all_rows = []
    unique_show_ids = set()
    region_category_counts = defaultdict(int)

    failed_requests = []

    for country in sorted(set(Three + Seventeen)):
        if country in Seventeen:
            categories = CATEGORIES_20
        else:
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

                # Episode info only for top_episodes
                if category == "top_episodes":
                    episode_uri = item.get("episodeUri", "")
                    episode_id = episode_uri.split(":")[-1] if episode_uri else ""
                    episode_name = item.get("episodeName", "")
                else:
                    episode_id = ""
                    episode_name = ""

                all_rows.append([
                    country,
                    category,
                    idx,
                    item.get("showName", ""),
                    item.get("showPublisher", ""),
                    item.get("showImageUrl", ""),
                    item.get("showDescription", ""),
                    item.get("chartRankMove", ""),
                    show_id,
                    episode_id,
                    episode_name
                ])

                if show_id:
                    unique_show_ids.add(show_id)

            region_category_counts[(country, category)] = len(items)
            time.sleep(0.5)

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

            if category == "top_episodes":
                episode_uri = item.get("episodeUri", "")
                episode_id = episode_uri.split(":")[-1] if episode_uri else ""
                episode_name = item.get("episodeName", "")
            else:
                episode_id = ""
                episode_name = ""

            all_rows.append([
                country,
                category,
                idx,
                item.get("showName", ""),
                item.get("showPublisher", ""),
                item.get("showImageUrl", ""),
                item.get("showDescription", ""),
                item.get("chartRankMove", ""),
                show_id,
                episode_id,
                episode_name
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

    print(f"\n[DONE] Saved {len(all_rows)} rows to 14_08_with_top_episodes.csv")
    print(f"[SUMMARY] Total entries: {len(all_rows)}")
    print(f"[SUMMARY] Unique shows: {len(unique_show_ids)}")

    print("\n[SUMMARY] Podcasts per region-category:")
    for (region, category), count in sorted(region_category_counts.items()):
        print(f"{region.upper()} - {category}: {count}")


if __name__ == "__main__":
    main()
