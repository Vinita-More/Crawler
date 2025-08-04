import requests
import gzip
import io
import re
import os
from bs4 import BeautifulSoup
import mysql.connector
import password  # file with: Password = "your_mysql_password"

# === DB connection ===
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=password.Password,
        database="store"
    )

def get_existing_ids_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT apple_id FROM id_bigint")
    ids = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return ids

# === Parse local sitemap XML ===
def get_gz_links_from_local_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "xml")
        gz_links = [loc.text for loc in soup.find_all("loc") if loc.text.endswith(".gz")]
        print(f"📄 {os.path.basename(filepath)}: Found {len(gz_links)} .gz links")
        return gz_links
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return []

# === Extract URLs from .gz ===
def extract_page_urls_from_gz(gz_url):
    try:
        response = requests.get(gz_url, timeout=10)
        with gzip.open(io.BytesIO(response.content), "rt", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "xml")
            return [loc.text for loc in soup.find_all("loc")]
    except Exception as e:
        print(f"❌ Error reading .gz URL {gz_url}: {e}")
        return []

# === Extract podcast IDs ===
def extract_podcast_ids_from_page(url):
    try:
        response = requests.get(url, timeout=10)
        return set(re.findall(r'/id(\d{5,})', response.text))
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return set()

# === Save new IDs ===
def save_new_ids_to_file(ids, filename="new_ids.txt"):
    with open(filename, "w") as f:
        for pid in ids:
            f.write(pid + "\n")
    print(f"✅ Saved {len(ids)} new IDs to {filename}")

# === Main ===
def main():
    # Local sitemap .xml files (update these paths)
    local_sitemaps = [
        "C:\\Users\\USER\\Desktop\\MillionPodcast_Crawler\\sitemaps\\sitemaps_podcasts_genre_1_1.xml",
        "C:\\Users\\USER\\Desktop\\\MillionPodcast_Crawler\\sitemaps\\sitemaps_podcasts_genre_1_2.xml"
    ]

    existing_ids = get_existing_ids_from_db()
    print(f"🗃️ Existing IDs in DB: {len(existing_ids)}")

    all_ids = set()

    for sitemap_path in local_sitemaps:
        gz_links = get_gz_links_from_local_file(sitemap_path)

        for gz_url in gz_links:
            print(f"➡️ Processing .gz file: {gz_url}")
            page_urls = extract_page_urls_from_gz(gz_url)
            print(f"   🔗 Found {len(page_urls)} page URLs")

            for page_url in page_urls:
                ids = extract_podcast_ids_from_page(page_url)
                all_ids.update(ids)

    print(f"🎧 Total scraped IDs: {len(all_ids)}")

    new_ids = all_ids - existing_ids
    print(f"🆕 New unique IDs: {len(new_ids)}")

    save_new_ids_to_file(new_ids)

if __name__ == "__main__":
    main()
