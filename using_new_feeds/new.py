import requests
import gzip
import io
import re
import xml.etree.ElementTree as ET
import csv
import sqlite3
from typing import Set, Tuple




def load_existing_csv_ids(csv_path: str) -> Set[str]:
    """Load existing Apple IDs from CSV file."""
    existing_ids = set()
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip():  # Check if row exists and first column is not empty
                    clean_id = row[0].strip()
                    if clean_id and clean_id.isdigit():  # Only add valid numeric IDs
                        existing_ids.add(clean_id)
        print(f"Loaded {len(existing_ids)} existing IDs from CSV")
    except FileNotFoundError:
        print(f"CSV file {csv_path} not found. Starting with empty set.")
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return existing_ids

def load_existing_db_ids(db_path: str) -> Set[str]:
    """Load existing Apple IDs from SQLite database."""
    existing_ids = set()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count for logging
        cursor.execute("SELECT COUNT(*) FROM podcasts;")
        total_count = cursor.fetchone()[0]
        print(f"Total number of entries in podcasts table: {total_count}")
        
        # Get existing iTunes IDs
        cursor.execute("""
            SELECT DISTINCT itunesId 
            FROM podcasts 
            WHERE itunesId IS NOT NULL 
              AND itunesId != '' 
              AND itunesId != '0'
        """)
        
        for row in cursor.fetchall():
            clean_id = str(row[0]).strip()
            if clean_id and clean_id.isdigit():  # Only add valid numeric IDs
                existing_ids.add(clean_id)
        
        conn.close()
        print(f"Loaded {len(existing_ids)} existing IDs from database")
    except Exception as e:
        print(f"Error loading from database: {e}")
    
    return existing_ids

def extract_gz_urls(sitemap_url: str) -> Set[str]:
    """Extract .gz URLs from sitemap index."""
    try:
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        gz_urls = set()  # Use set to avoid duplicate URLs
        for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            if loc.text and loc.text.strip().endswith(".gz"):
                gz_urls.add(loc.text.strip())
        
        return gz_urls
    except Exception as e:
        print(f"Error extracting .gz URLs from {sitemap_url}: {e}")
        return set()

def decompress_gz_and_parse(gz_url: str) -> Set[Tuple[str, str]]:
    """Download and parse a .gz sitemap file, returning (itunes_id, url) tuples."""
    try:
        response = requests.get(gz_url, timeout=60)
        response.raise_for_status()
        
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
            xml_data = gz.read()
        
        root = ET.fromstring(xml_data)
        results = set()  # Use set to avoid duplicates within this file
        
        for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            if loc.text:
                podcast_url = loc.text.strip()
                match = re.search(r'/id(\d+)', podcast_url)
                if match:
                    itunes_id = match.group(1)
                    # Validate iTunes ID (should be numeric and reasonable length)
                    if itunes_id.isdigit() and 1 <= len(itunes_id) <= 15:
                        results.add((itunes_id, podcast_url))
        
        return results
    except Exception as e:
        print(f"Error parsing {gz_url}: {e}")
        return set()

def write_ids_to_file(filename: str, id_set: Set[str]) -> None:
    """Write iTunes IDs to file, sorted and deduplicated."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Sort numerically for better organization
            sorted_ids = sorted(id_set, key=lambda x: int(x) if x.isdigit() else 0)
            for itunes_id in sorted_ids:
                f.write(f"{itunes_id}\n")
        print(f"Successfully wrote {len(id_set)} IDs to {filename}")
    except Exception as e:
        print(f"Error writing to {filename}: {e}")

def main():
    # Configuration
    CSV_PATH = "../apple_ids.csv"
    DB_PATH = "../using_database/podcastindex_feeds.db"
    SITEMAP_INDEX = 'https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml'
    
    # Step 1: Load existing IDs
    print("Loading existing IDs...")
    existing_ids_csv = load_existing_csv_ids(CSV_PATH)
    existing_ids_db = load_existing_db_ids(DB_PATH)
    
    # Step 2: Get .gz URLs (deduplicated)
    print("Extracting .gz URLs from sitemap index...")
    gz_urls = extract_gz_urls(SITEMAP_INDEX)
    print(f"Found {len(gz_urls)} unique .gz files")
    
    if not gz_urls:
        print("No .gz files found. Exiting.")
        return
    
    # Step 3: Extract and deduplicate all iTunes IDs
    print("Processing .gz files...")
    all_results = set()  # Global set to avoid duplicates across all files
    
    for i, url in enumerate(gz_urls, 1):
        print(f"Processing file {i}/{len(gz_urls)}: {url}")
        results = decompress_gz_and_parse(url)
        
        # Track duplicates within this file vs global set
        before_count = len(all_results)
        all_results.update(results)
        after_count = len(all_results)
        new_in_file = after_count - before_count
        
        print(f"File {i}: Found {len(results)} podcasts, {new_in_file} new unique IDs")
    
    # Step 4: Extract just the iTunes IDs from the result tuples
    all_ids = {itunes_id for itunes_id, _ in all_results}
    print(f"Total unique iTunes IDs found: {len(all_ids)}")
    
    # Step 5: Compare and filter (using set operations for efficiency)
    new_ids_csv_only = all_ids - existing_ids_csv
    new_ids_db_only = all_ids - existing_ids_db
    new_ids_both = all_ids - (existing_ids_csv | existing_ids_db)  # Union operation
    
    # Step 6: Write results to files
    print("Writing results to files...")
    write_ids_to_file("new_ids_not_in_csv.txt", new_ids_csv_only)
    write_ids_to_file("new_ids_not_in_db.txt", new_ids_db_only)
    write_ids_to_file("new_ids_not_in_csv_and_db.txt", new_ids_both)
    
    # Step 7: Summary
    print("="*50)
    print("SUMMARY:")
    print(f"✅ Total unique iTunes IDs discovered: {len(all_ids):,}")
    print(f"✅ Already in CSV: {len(existing_ids_csv):,}")
    print(f"✅ Already in DB: {len(existing_ids_db):,}")
    print(f"✅ New IDs not in CSV: {len(new_ids_csv_only):,}")
    print(f"✅ New IDs not in DB: {len(new_ids_db_only):,}")
    print(f"✅ New IDs not in both CSV and DB: {len(new_ids_both):,}")
    print("="*50)

if __name__ == "__main__":
    main()

# import requests
# import gzip
# import io
# import re
# import xml.etree.ElementTree as ET
# import csv
# import sqlite3

# # Load existing Apple IDs from CSV
# with open("../apple_ids.csv", "r", encoding="utf-8") as csvfile:
#     reader = csv.reader(csvfile)
#     existing_ids_csv = {row[0].strip() for row in reader if row}

# # Connect to SQLite database (adjust path as needed)
# conn = sqlite3.connect("../using_database/podcastindex_feeds.db")
# cursor = conn.cursor()

# cursor.execute("SELECT COUNT(*) FROM podcasts;")
# print("Total number of entries in podcasts table:", cursor.fetchone()[0])

# cursor.execute("""
#     SELECT itunesId 
#     FROM podcasts 
#     WHERE itunesId IS NOT NULL 
#       AND itunesId != '' 
#       AND itunesId != '0'
# """)
# existing_ids_db = {str(row[0]).strip() for row in cursor.fetchall()}

# def extract_gz_urls(sitemap_url):
#     response = requests.get(sitemap_url)
#     response.raise_for_status()
#     root = ET.fromstring(response.content)
#     return [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if loc.text.endswith(".gz")]

# def decompress_gz_and_parse(gz_url):
#     response = requests.get(gz_url)
#     response.raise_for_status()
#     with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
#         xml_data = gz.read()

#     try:
#         root = ET.fromstring(xml_data)
#         urls = set()
#         for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
#             podcast_url = loc.text.strip()
#             match = re.search(r'/id(\d+)', podcast_url)
#             if match:
#                 itunes_id = match.group(1)
#                 urls.add((itunes_id, podcast_url))  # Add tuple of ID + URL
#         return urls
#     except ET.ParseError as e:
#         print(f"Error parsing {gz_url}: {e}")
#         return set()

# # Step 1: Get .gz URLs
# sitemap_index = 'https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml'
# gz_urls = extract_gz_urls(sitemap_index)
# print(f"Found {len(gz_urls)} .gz files")

# # Step 2: Extract and deduplicate all iTunes IDs
# all_results = set()
# for url in gz_urls:
#     results = decompress_gz_and_parse(url)
#     all_results.update(results)
#     print(f"Extracted {len(results)} podcasts from {url}")

# # Step 3: Extract just the iTunes IDs from the result tuples
# all_ids = {itunes_id for itunes_id, _ in all_results}

# # Step 4: Compare and filter
# new_ids_csv_only = all_ids - existing_ids_csv
# new_ids_db_only = all_ids - existing_ids_db
# new_ids_both = all_ids - (existing_ids_csv.union(existing_ids_db))

# # Step 5: Write to files
# def write_ids_to_file(filename, id_set):
#     with open(filename, "w", encoding="utf-8") as f:
#         for itunes_id in sorted(id_set):
#             f.write(f"{itunes_id}\n")

# write_ids_to_file("new_ids_not_in_csv.txt", new_ids_csv_only)
# write_ids_to_file("new_ids_not_in_db.txt", new_ids_db_only)
# write_ids_to_file("new_ids_not_in_csv_and_db.txt", new_ids_both)

# # Summary
# print(f"✅ New IDs not in CSV: {len(new_ids_csv_only)}")
# print(f"✅ New IDs not in DB: {len(new_ids_db_only)}")
# print(f"✅ New IDs not in both: {len(new_ids_both)}")





# import requests
# import gzip
# import io
# import re
# import xml.etree.ElementTree as ET
# import csv
# import sqlite3

# old_data = "../apple_ids.csv"

# # Load existing Apple IDs from CSV
# with open(old_data, "r", encoding="utf-8") as csvfile:
#     reader = csv.reader(csvfile)
#     existing_ids_csv = {row[0].strip() for row in reader if row}

# # Connect to SQLite database
# conn = sqlite3.connect("../using_database/podcastindex_feeds.db")
# cursor = conn.cursor()

# cursor.execute("SELECT COUNT(*) FROM podcasts;")
# count = cursor.fetchone()[0]
# print("Total number of entries in podcasts table:", count)

# # Fetch all non-null itunesIds from the database
# cursor.execute("""
#     SELECT itunesId 
#     FROM podcasts 
#     WHERE itunesId IS NOT NULL 
#       AND itunesId != '' 
#       AND itunesId != '0'
# """)
# existing_ids_db = {str(row[0]).strip() for row in cursor.fetchall()}

# # Combine existing IDs from CSV and DB
# #existing_ids = existing_ids_csv.union(existing_ids_db)

# def extract_gz_urls(sitemap_url):
#     response = requests.get(sitemap_url)
#     response.raise_for_status()
#     root = ET.fromstring(response.content)
#     return [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if loc.text.endswith(".gz")]

# def decompress_gz_and_parse(gz_url):
#     response = requests.get(gz_url)
#     response.raise_for_status()
#     with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
#         xml_data = gz.read()

#     try:
#         root = ET.fromstring(xml_data)
#         urls = set()
#         for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
#             podcast_url = loc.text.strip()
#             match = re.search(r'/id(\d+)', podcast_url)
#             if match:
#                 itunes_id = match.group(1)
#                 urls.add((itunes_id, podcast_url))
#         return urls
#     except ET.ParseError as e:
#         print(f"Error parsing {gz_url}: {e}")
#         return []

# # Start processing
# sitemap_index = 'https://podcasts.apple.com/sitemaps_podcasts_index_podcast_1.xml'
# gz_urls = extract_gz_urls(sitemap_index)

# print(f"Found {len(gz_urls)} .gz files")

# all_results = []
# for url in gz_urls:
#     results = decompress_gz_and_parse(url)
#     all_results.extend(results)
#     print(f"Extracted {len(results)} podcasts from {url}")

# # Filter new unique IDs (not in CSV or DB)
# new_ids = {itunes_id for itunes_id, _ in all_results if itunes_id not in existing_ids}

# print(f"Found {len(new_ids)} new iTunes IDs")

# # Save to new.txt
# with open("new.txt", "w", encoding="utf-8") as f:
#     for itunes_id in sorted(new_ids):
#         f.write(f"{itunes_id}\n")

# print("Saved new iTunes IDs to new.txt")
