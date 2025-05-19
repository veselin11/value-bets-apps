import requests
from datetime import datetime

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

# Зареждане на всички поддържани спортове от The Odds API
sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
sports_response = requests.get(sports_url)
sports = sports_response.json()

print("Автоматичен детектор на стойностни футболни залози с форма и H2H\n")

for sport in sports:
    sport_key = sport['key']
    sport_title = sport['title']
    print(f"Лига: {sport_title}")

    odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "eu",
        "markets": "h2h,totals,btts",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "daysFrom": 0,
        "daysTo": 3,
        "apiKey": ODDS_API_KEY
    }

    try:
        odds_response = requests.get(odds_url, params=params)
        odds_response.raise_for_status()
        matches = odds_response.json()

        if not matches:
            print("  Няма мачове или грешка при зареждане.\n")
            continue

        print(f"  Намерени мачове: {len(matches)}")

        for match in matches:
            home = match['home_team']
            away = match['away_team']
            start_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
            print(f"  {home} vs {away} - {start_time}")

    except requests.exceptions.RequestException as e:
        print(f"Грешка при зареждане на коефициенти: {e}")
