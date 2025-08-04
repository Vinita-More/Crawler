# To simply insert values of appleids into the  (no validation performed)
import pandas as pd
import mysql.connector
import password

# Step 1: Read the CSV safely
df = pd.read_csv("apple_ids.csv", dtype=str)
print("Columns found:", df.columns)

# If it has no header, add one manually
if df.columns[0].startswith("Unnamed"):
    df.columns = ["apple_id"]

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
print(f"✅ Total appleids in table: {count}")

# Clean up
cursor.close()
conn.close()