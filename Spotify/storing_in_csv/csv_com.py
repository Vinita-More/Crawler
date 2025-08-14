# comparison with top episodes
import csv

# File paths
old_file = "13_08_with_top_episodes.csv"                         # yesterday's data
new_file = "14_08_with_top_episodes.csv"                             # today's data
output_file = "14_08_rank_changes.csv"
all_columns = set()
# Read yesterday's data into a dictionary with dynamic keys
old_data = {}
with open(old_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_columns.update(row.keys())
        if row["Category"] == "top_episodes":
            key = (row["Region"], row["Category"], row["ShowID"], row["EpisodeID"])
        else:
            key = (row["Region"], row["Category"], row["ShowID"])
        old_data[key] = int(row["Rank"])

# Read today's data and calculate movement
new_data = []
with open(new_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_columns.update(row.keys())
        if row["Category"] == "top_episodes":
            key = (row["Region"], row["Category"], row["ShowID"], row["EpisodeID"])
        else:
            key = (row["Region"], row["Category"], row["ShowID"])
        today_rank = int(row["Rank"])
        yesterday_rank = old_data.get(key)

        # Determine movement
        if yesterday_rank is None:
            movement = "NEW"
        else:
            diff = yesterday_rank - today_rank
            if diff > 0:
                movement = f"+{diff}"
            elif diff < 0:
                movement = f"{diff}"
            else:
                movement = "0"

        row["ChartRankMove"] = movement
        new_data.append(row)

# Check for items that dropped out
max_rank_today = max(int(row["Rank"]) for row in new_data)
dropped_out_count = 0
existing_keys_today = set()
for row in new_data:
    if row["Category"] == "top_episodes":
        existing_keys_today.add((row["Region"], row["Category"], row["ShowID"], row["EpisodeID"], row["EpisodeName"]))
    else:
        existing_keys_today.add((row["Region"], row["Category"], row["ShowID"]))

for key, yesterday_rank in old_data.items():
    if key not in existing_keys_today:
        dropped_out_count += 1
        if len(key) == 4:  # top_episodes
            region, category, show_id, episode_id = key
        else:
            region, category, show_id = key
            episode_id = ""
            episode_name = ""
        new_data.append({
            "Region": region,
            "Category": category,
            "Rank": max_rank_today + dropped_out_count,
            "ShowName": "",
            "Publisher": "",
            "ImageURL": "",
            "Description": "",
            "ChartRankMove": "DOWN_OUT",
            "ShowID": show_id,
            "EpisodeID": episode_id,
            "EpisodeName": episode_name
        })

# Write updated data
fieldnames = ["Region", "Category", "Rank", "ShowName", "Publisher", "ImageURL", "Description", "ChartRankMove", "ShowID", "EpisodeID","EpisodeName"]
with open(output_file, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(new_data)

print(f"✅ Rank comparison done! Output saved to {output_file}")
