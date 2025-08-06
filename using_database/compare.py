import sqlite3
import csv


old_data = "itunes_ids.txt"

# Load existing Apple IDs from TXT (one ID per line)
with open(old_data, "r", encoding="utf-8") as f:
    existing_ids = {line.strip() for line in f if line.strip()}

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
new_ids = existing_ids - db_ids


# Output result
print(f"Total itunesIds in DB: {len(db_ids)}")
print(f"Total ituneIds in CSV: {len(existing_ids)}")
print(f"Found {len(new_ids)} new Apple IDs to verify...")
    
# Save only valid Apple IDs
with open("new_06_08_2.csv", "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for apple_id in new_ids:
            writer.writerow([apple_id])
           
