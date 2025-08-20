import requests

url = "https://podcastcharts.byspotify.com/api/charts/top?region=es"

resp = requests.get(url)
data = resp.json()

# Spotify nests categories inside "categories" → "items"
count = len(data)
print(f"Number of categories: {count}")


