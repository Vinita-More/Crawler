import requests

url = "https://podcastcharts.byspotify.com/api/charts/top?region=ao"

resp = requests.get(url)
data = resp.json()

# Spotify nests categories inside "categories" → "items"
count = len(data)
print(f"Number of entries: {count}")


