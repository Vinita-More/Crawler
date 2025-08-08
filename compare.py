
import csv
import os

CSV_FILENAME = "apple_ids.csv"
new_file = "using_gzip_files/new.txt"

# Load existing podcast IDs from CSV
def load_existing_ids(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        return {row[0] for row in reader if row}
    
# Load existing Apple IDs from TXT (one ID per line)
with open(new_file, "r", encoding="utf-8") as f:
    new_ids = {line.strip() for line in f if line.strip()}

# existing ids
existing_ids = load_existing_ids(CSV_FILENAME)


# Compare to find new IDs
unique_ids = new_ids - existing_ids


# Output result
print(f"Total itunesIds in CSV: {len(existing_ids)}")
print(f"Total ituneIds in TXT: {len(new_ids)}")
print(f"Found {len(unique_ids)} new Apple IDs to verify...")
    
# Save only valid Apple IDs
with open("new_08_08_2.csv", "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for apple_id in new_ids:
            writer.writerow([apple_id])
           
