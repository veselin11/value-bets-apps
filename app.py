import streamlit as st
import requests
from datetime import datetime

st.title("Детектор на стойностни футболни залози")

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

def get_matches(sport_key, markets):
    odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "eu",
        "markets": markets,
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "daysFrom": 0,
        "daysTo": 3,
        "apiKey": ODDS_API_KEY
    }
    try:
        response = requests.get(odds_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 422 and ',' in markets:
            # Ако има няколко пазара и има грешка, пробваме само с 'h2h'
            if markets != "h2h":
                st.warning(f"Пазарите '{markets}' не са налични, опитвам само с 'h2h'.")
                return get_matches(sport_key, "h2h")
        st.warning(f"Пропуснат спорт с ключ {sport_key} за пазар {markets} (грешка {response.status_code})")
        return []

try:
    sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    response = requests.get(sports_url)
    response.raise_for_status()
    sports = response.json()

    football_sports = [sport for sport in sports if "soccer" in sport['key'].lower()]
    if not football_sports:
        st.write("Не са намерени футболни спортове.")
    else:
        for sport in football_sports:
            sport_key = sport['key']
            sport_title = sport['title']
            st.write(f"Лига: {sport_title}")

            matches = get_matches(sport_key, "h2h,totals,btts")
            if not matches:
                st.write("  Няма мачове или грешка при зареждане.")
                continue

            st.write(f"  Намерени мачове: {len(matches)}")
            for match in matches:
                home = match['home_team']
                away = match['away_team']
                start_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                st.write(f"  {home} vs {away} - {start_time}")

except Exception as e:
    st.error(f"Грешка: {e}")
