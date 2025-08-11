import requests
import base64
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import password 
CLIENT_ID = password.CLIENT_ID
CLIENT_SECRET = password.CLIENT_SECRET

# Encode client credentials
auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

# Get token
token_url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {b64_auth_str}"
}
data = {
    "grant_type": "client_credentials"
}
response = requests.post(token_url, headers=headers, data=data)
access_token = response.json()["access_token"]

print("Access Token:", access_token)

show_id = "4IRmcxkSPkYQcWUleBh71A"  # example podcast ID
url = f"https://api.spotify.com/v1/shows/{show_id}?market=US"
headers = {
    "Authorization": f"Bearer {access_token}"
}
res = requests.get(url, headers=headers)
data = res.json()
print(data)

