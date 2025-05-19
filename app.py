import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

url = "https://api.the-odds-api.com/v4/sports"
params = {"apiKey": API_KEY}

response = requests.get(url, params=params)
sports = response.json()

for sport in sports:
    if "soccer" in sport['key']:
        print(f"{sport['key']} - {sport['title']}")
