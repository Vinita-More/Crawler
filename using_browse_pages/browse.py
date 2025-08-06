import requests
from bs4 import BeautifulSoup
import re

country= [
    "us", "gb", "ca", "au", "in", "de", "fr", "jp", "kr", "br", "mx", "cn", "it", "es",
    "ru", "nl", "se", "no", "fi", "dk", "ie", "nz", "za", "sg", "hk", "tw", "be", "ch",
    "at", "pl", "tr", "sa", "ae", "ar", "cl", "co", "cz", "gr", "hu", "id", "il", "my",
    "ph", "pt", "ro", "sk", "th", "ua", "ve", "vn", "az"
]

urls = []
def generate_urls(country):
    for country in country:
        new_url = f"https://podcasts.apple.com/{country}/browse"
        urls.append(new_url)


headers = {
    "User-Agent": "Mozilla/5.0"  # mimic browser
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <a> tags within divs of class 'shelf-content'
anchors = soup.select('div.shelf-content a[href]')
count = 0
ids = set()
for a in anchors:
    href = a['href']
    match = re.search(r'/id(\d+)', href)
    if match:
        ids.add(match.group(1))
        count = count + 1

# Print the found Apple Podcast IDs
print("Found Apple Podcast IDs:")
for podcast_id in ids:
    print(podcast_id)
print(count)
