# To get the ids that are dropped due to being a string and adding the rest to the database (just printing them)
import pandas as pd
import mysql.connector
import password

# Step 1: Read the CSV safely
df = pd.read_csv("apple_ids.csv", dtype=str)
print("Columns found:", df.columns)

# If it has no header, add one manually
if df.columns[0].startswith("Unnamed"):
    df.columns = ["apple_id"]

skipped_entries = []

def is_valid_apple_id(val):
    if isinstance(val, str) and val.isdigit() and len(val) <= 20:
        return True
    skipped_entries.append(val) 
    return False

valid_df = df[df['apple_id'].apply(is_valid_apple_id)]

print(f"✅ Valid apple_ids found: {len(valid_df)}")
print(f"❌ Skipped invalid entries: {len(df) - len(valid_df)}")
for s in skipped_entries:
    print(f" - {s}")

# Step 2: Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password.Password,
    database="store"
)
cursor = conn.cursor()

# Step 3: Insert
insert_query = "INSERT IGNORE INTO podcast (apple_id) VALUES (%s)"
data = [(str(row['apple_id']),) for _, row in df.iterrows()]
cursor.executemany(insert_query, data)
conn.commit()

# Step 4: Count
cursor.execute("SELECT COUNT(*) FROM podcast")
count = cursor.fetchone()[0]
print(f"✅ Total apple_ids in table: {count}")

# Clean up
cursor.close()
conn.close()