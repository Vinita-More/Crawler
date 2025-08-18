import requests

url = "https://podcastcharts.byspotify.com/api/charts/trending?region=us"

resp = requests.get(url)
data = resp.json()

# Spotify nests categories inside "categories" → "items"
count = len(data)
print(f"Number of categories: {count}")
