import pandas as pd
import mysql.connector
from mysql.connector import Error
import password

# Load CSV
df = pd.read_csv("apple_ids.csv")

# Clean and drop rows with invalid apple_id
df = df[pd.to_numeric(df['apple_id'], errors='coerce').notnull()]  # Keep only numeric
df['apple_id'] = df['apple_id'].astype('int')  # Convert to int

inserted = 0
skipped = 0

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=password.Password,
        database='store'
    )

    cursor = conn.cursor()

    for apple_id in df['apple_id']:
        try:
            cursor.execute("INSERT IGNORE INTO id_bigint (apple_id) VALUES (%s)", (apple_id,))
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error inserting {apple_id}: {e}")
            skipped += 1

    conn.commit()

except Error as e:
    print("MySQL connection error:", e)

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

print(f"✅ Inserted: {inserted}")
print(f"🚫 Skipped (duplicates or errors): {skipped}")
