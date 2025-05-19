import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

# Взимаме всички спортове
sports_url = "https://api.the-odds-api.com/v4/sports"
sports_response = requests.get(sports_url, params={"apiKey": API_KEY})
sports = sports_response.json()

# Филтрираме само футболни лиги, които имат пазари (is_active = True)
soccer_leagues = [s for s in sports if "soccer" in s["key"] and s["active"]]

# Извеждаме всички налични активни футболни лиги
print("Налични активни футболни лиги днес:")
for league in soccer_leagues:
    print(f"- {league['title']} ({league['key']})")
