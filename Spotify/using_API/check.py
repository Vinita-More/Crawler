import requests

url = "https://podcastcharts.byspotify.com/api/charts/top?region=zw" 


resp = requests.get(url)
data = resp.json()

# Spotify nests categories inside "categories" → "items"
count = len(data)
print(f"Number of categories: {count}")
