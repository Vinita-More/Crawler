import requests

url = "https://podcastcharts.byspotify.com/api/charts/trending?region=es"
response = requests.get(url)
data = response.json()

# Check length of top-level JSON array/object
if isinstance(data, list):
    print(f"Length of JSON list: {len(data)}")
elif isinstance(data, dict):
    print(f"Top-level keys: {list(data.keys())}")
    for key, value in data.items():
        if isinstance(value, list):
            print(f"Length of '{key}': {len(value)}")
else:
    print("Unknown JSON structure")
