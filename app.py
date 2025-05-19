import streamlit as st
import requests
from datetime import datetime

st.title("Автоматичен детектор на стойностни залози")

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

try:
    sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    response = requests.get(sports_url)
    response.raise_for_status()
    sports = response.json()
    st.write(f"Намерени спортове: {len(sports)}")

    for sport in sports:
        sport_key = sport['key']
        sport_title = sport['title']
        st.write(f"Лига: {sport_title}")

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
        odds_response = requests.get(odds_url, params=params)
        odds_response.raise_for_status()
        matches = odds_response.json()
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
