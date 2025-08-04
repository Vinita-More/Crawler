from bs4 import BeautifulSoup
import re
import csv
import json


# to get podcast_ids from the sitemap
def get_podcast_ids_from_local_file(file_path):
    
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    soup = BeautifulSoup(content, "lxml-xml")  
    loc_tags = soup.find_all("loc")

    podcast_ids = []
    
    for loc in loc_tags:
        url = loc.text.strip()

        # Regex to match `/id/` followed by digits
        match = re.search(r"id(\d+)", url)
        if match:
            podcast_id = match.group(1)
            podcast_ids.append(podcast_id)
            
    return podcast_ids


# to store podcast_ids in json
def save_to_json(podcast_ids, filename="podcast_ids.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted(podcast_ids), f, indent=4)


# to store podcast_ids in csv
def save_to_csv(podcast_ids, filename="podcastid.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Podcast ID"])  
        for pid in podcast_ids:
            writer.writerow([pid])


# definig file path of sitemap
file_path = "sitemaps_podcasts_podcast_100_1.xml"

# function call to get ids from sitemap
podcast_ids = get_podcast_ids_from_local_file(file_path)

# converting ids to set to retain only unique ids
podcast_ids_set = set(podcast_ids)

#print(podcast_ids_set length)
print("length", len(podcast_ids_set))

# saving ids in json format
save_to_json(podcast_ids_set)
save_to_csv(podcast_ids_set)

