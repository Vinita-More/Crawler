import sqlite3
import csv
import requests
from bs4 import BeautifulSoup

old_data = "../apple_ids.csv"

# Load existing Apple IDs from CSV
with open(old_data, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    existing_ids = {row[0].strip() for row in reader if row}

# Connect to SQLite database
conn = sqlite3.connect("podcastindex_feeds.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM podcasts;")
count = cursor.fetchone()[0]
print("Total number of entries in podcasts table:", count)

# Fetch all non-null itunesIds from the database
cursor.execute("""
    SELECT itunesId 
    FROM podcasts 
    WHERE itunesId IS NOT NULL 
      AND itunesId != '' 
      AND itunesId != '0'
""")
db_ids = {str(row[0]).strip() for row in cursor.fetchall()}

# Compare to find new IDs
new_ids = db_ids - existing_ids

# Output result
print(f"Total itunesIds in DB: {len(db_ids)}")
print(f"Total ituneIds in CSV: {len(existing_ids)}")
print(f"Found {len(new_ids)} new Apple IDs to verify...")
    
# Save only valid Apple IDs
with open("new_apple_ids.csv", "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for apple_id in new_ids:
            writer.writerow([apple_id])
           
# def is_valid_apple_id(apple_id):
#     url = f"https://podcasts.apple.com/podcast/id{apple_id}"
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             return False

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Get the <head> section
#         head = soup.find("head")
#         if not head:
#             return False

#         # Ensure <title> exists within <head>
#         title_tag = head.find("title")
#         if not title_tag:
#             return False

#         # Optional: check for 404 phrases in title
#         if "not found" in title_tag.text.lower() or "can’t be found" in title_tag.text.lower():
#             return False

#         return True

#     except requests.RequestException as e:
#         print(f"⚠️ Error checking ID {apple_id}: {e}")
#         return False

# def is_valid_apple_id(apple_id):
#     url = f"https://podcasts.apple.com/podcast/id{apple_id}"
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             return False

#         soup = BeautifulSoup(response.text, "html.parser")
        
#         # Look for a title that includes "Apple Podcasts" (valid pages usually have this)
#         title = soup.find("title")
#         if not title or "Apple Podcasts" not in title.text:
#             return False

#         # Optional: Look for the podcast name in a meta tag
#         meta = soup.find("meta", {"property": "og:title"})
#         if not meta or not meta.get("content"):
#             return False

#         return True

#     except requests.RequestException as e:
#         print(f"⚠️ Error checking ID {apple_id}: {e}")
#         return False


# OLD_CSV = "../apple_ids.csv"
# # Connect to the SQLite database
# conn = sqlite3.connect("podcastindex_feeds.db")
# cursor = conn.cursor()

# # Check available tables
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

# cursor.execute("SELECT COUNT(*) FROM podcasts;")
# count = cursor.fetchone()[0]
# print("Total number of entries in podcasts table:", count)

# cursor.execute("""
#     SELECT itunesId 
#     FROM podcasts 
#     WHERE itunesId IS NOT NULL 
#       AND TRIM(itunesId) != '' 
#       AND itunesId != '0'
# """)
# itunes_ids = cursor.fetchall()
# print(len(itunes_ids))


# # Load existing Apple IDs from CSV
# with open(OLD_CSV, "r", encoding="utf-8") as csvfile:
#     reader = csv.reader(csvfile)
#     existing_ids = {row[0].strip() for row in reader if row} 


# for id_tuple in itunes_ids:
#     print(id_tuple[0])




# cursor.execute("PRAGMA table_info(podcasts);")
# columns = cursor.fetchall()
# for col in columns:
#     print(col)



# import sqlite3

# def recover_db(bad_db_path, new_db_path):
#     try:
#         # Connect to the corrupted DB
#         bad_db = sqlite3.connect(bad_db_path)
#         bad_cursor = bad_db.cursor()

#         # Connect to a new good DB
#         new_db = sqlite3.connect(new_db_path)
#         new_cursor = new_db.cursor()

#         # Get tables
#         bad_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         tables = bad_cursor.fetchall()

#         for table_name in tables:
#             table = table_name[0]
#             try:
#                 # Copy table schema
#                 bad_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
#                 create_table_sql = bad_cursor.fetchone()[0]
#                 new_cursor.execute(create_table_sql)

#                 # Copy data
#                 bad_cursor.execute(f"SELECT * FROM {table}")
#                 rows = bad_cursor.fetchall()

#                 placeholders = ','.join(['?'] * len(rows[0]))
#                 new_cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
#                 new_db.commit()
#                 print(f"Recovered table: {table}")
#             except Exception as e:
#                 print(f"Failed to recover table {table}: {e}")

#         bad_db.close()
#         new_db.close()

#     except Exception as e:
#         print("Recovery failed:", e)

# recover_db("podcastindex_feeds.db", "recovered.db")
