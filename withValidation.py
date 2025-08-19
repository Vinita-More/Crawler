# Inserting values with validation into varchar to avoid taking string entry

import pandas as pd
import mysql.connector
import password

# Step 1: Read CSV
df = pd.read_csv("apple_ids.csv", dtype=str)
print("Columns found:", df.columns)


if df.columns[0].startswith("Unnamed"):
    df.columns = ["apple_id"]

# Step 1.5: Validate and store invalid entries
skipped_entries = []

def is_valid_apple_id(val):
    if isinstance(val, str) and val.isdigit() and len(val) <= 20:
        return True
    skipped_entries.append(val)
    return False

valid_df = df[df['apple_id'].apply(is_valid_apple_id)]

print(f"✅ Valid apple_ids found: {len(valid_df)}")
print(f"❌ Skipped invalid entries: {len(skipped_entries)}")

# Step 2: Connect to DB
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password.Password,
    database="store"
)
cursor = conn.cursor()

# Step 3: Insert clean data
insert_query = "INSERT IGNORE INTO podcast (apple_id) VALUES (%s)"
data = [(row['apple_id'],) for _, row in valid_df.iterrows()]
cursor.executemany(insert_query, data)
conn.commit()

# Step 4: Final count
cursor.execute("SELECT COUNT(*) FROM podcast")
count = cursor.fetchone()[0]
print(f"✅ Total apple_ids in table: {count}")

# Step 5: Show skipped values
if skipped_entries:
    print("\n❌ Skipped apple_ids:")
    for s in skipped_entries:
        print(f" - {s}")

# Cleanup
cursor.close()
conn.close()
