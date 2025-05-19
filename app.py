import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

# Лиги, които искаме да проверим
leagues = [
    "soccer_bulgaria_pfl",
    "soccer_croatia_prva_hnl",
    "soccer_poland_ekstraklasa",
    "soccer_romania_liga_i",
]

# Различни региони за търсене (можеш да добавиш още)
regions = ["eu", "uk", "us"]

# Пазари, които търсим
markets = ["h2h", "totals", "spreads"]

def fetch_odds(league, region, market):
    url = f"https://api.the-odds-api.com/v4/sports/{league}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": region,
        "markets": market,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Грешка при заявка за {league} - {region} - {market}: {response.status_code}")
        return []
    return response.json()

for league in leagues:
    print(f"\n=== {league} ===")
    found_any = False
    for region in regions:
        for market in markets:
            matches = fetch_odds(league, region, market)
            if matches:
                found_any = True
                print(f"Регион: {region}, Пазар: {market}, Мачове: {len(matches)}")
                for match in matches:
                    teams = match.get("teams", [])
                    commence_time = match.get("commence_time", "unknown")
                    print(f"  {teams} - {commence_time}")
    if not found_any:
        print("  Няма намерени мачове за тази лига.")
