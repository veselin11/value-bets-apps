import requests
from datetime import datetime

print("Старт на скрипта...")

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

try:
    sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    sports_response = requests.get(sports_url)
    print("Статус код:", sports_response.status_code)
    sports = sports_response.json()
    print(f"Намерен брой спортове: {len(sports)}")

    for sport in sports:
        sport_key = sport['key']
        sport_title = sport['title']
        print(f"Лига: {sport_title}")

        # Продължаваш с останалия код...

except Exception as e:
    print(f"Възникна грешка: {e}")
