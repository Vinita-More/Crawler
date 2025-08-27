import mysql.connector
import password

# Database connection
conn = mysql.connector.connect(
    host=password.dbhost,
    user=password.dbuser,
    password=password.dbpass,
    database=password.dbname
)
cursor = conn.cursor()

# Tables to compare
table1 = "spotify_charts_20250827_080606"
table2 = "spotify_charts_20250827_131212"

# Define the key columns for comparison
key_columns = ["showId", "countryCode", "category", "chart_rank"]

# Build SELECT queries
columns_str = ", ".join(key_columns)

query1 = f"SELECT {columns_str} FROM {table1}"
query2 = f"SELECT {columns_str} FROM {table2}"

# Fetch data
cursor.execute(query1)
data1 = set(cursor.fetchall())

cursor.execute(query2)
data2 = set(cursor.fetchall())

# Find differences
only_in_table1 = data1 - data2
only_in_table2 = data2 - data1

# Save results to file
with open("different.txt", "w", encoding="utf-8") as f:
    f.write(f"--- Present in {table1} but not in {table2} ---\n")
    for row in only_in_table1:
        f.write(str(row) + "\n")

    f.write(f"\n--- Present in {table2} but not in {table1} ---\n")
    for row in only_in_table2:
        f.write(str(row) + "\n")

print("Comparison complete. Differences saved to different.txt")

# Cleanup
cursor.close()
conn.close()
