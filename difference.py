# To get ids that are unique in the new list of IDs
import json
import mysql.connector
from datetime import datetime
import password

# MySQL DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password.Password,
    database="store"
)
cursor = db.cursor()

# Step 2: Load existing IDs from DB
cursor.execute("SELECT apple_id FROM apple_ids")
existing_ids = set(str(row[0]) for row in cursor.fetchall())

# Step 3: Load new IDs from JSON list
def load_ids_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return set(json.load(f))  # Already a list of strings

json_ids = load_ids_from_json("podcast_ids.json")

# Step 4: Compare and find new IDs
new_ids = json_ids - existing_ids

# Step 5: Insert new IDs into `new_ids` table with timestamp
if new_ids:
    print(f"Found {len(new_ids)} new IDs. \nInserting into database...")
    for aid in new_ids:
        cursor.execute(
            "INSERT INTO new_ids (apple_id, discovered_at) VALUES (%s, %s)",
            (int(aid), datetime.now())
        )
    db.commit()
    print("Insertion complete.")
else:
    print("No new IDs found.")


# Cleanup
cursor.close()
db.close()