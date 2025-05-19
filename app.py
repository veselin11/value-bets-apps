import streamlit as st
import requests
from datetime import datetime
import pytz

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

st.title("Филтриране на футболни мачове по първенства")

# Избрани първенства (примерни имена, точно съвпадение с API)
wanted_leagues = [
    "English Premier League",
    "Spanish La Liga",
    "German Bundesliga",
    "Italian Serie A",
    "French Ligue 1",
    "UEFA Champions League"
]

url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 2,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()
    filtered_matches = []

    for match in matches:
        league = match.get("sport_title") or match.get("league") or ""
        if league in wanted_leagues:
            filtered_matches.append(match)

    st.write(f"Намерени мачове от избрани първенства: {len(filtered_matches)}")

    for match in filtered_matches:
        home = match["home_team"]
        away = match["away_team"]
        league = match.get("sport_title") or match.get("league") or "Unknown League"
        time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))
        
        st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')}) - {league}")
        
        for bookmaker in match["bookmakers"]:
            st.markdown(f"**{bookmaker['title']}**")
            for market in bookmaker["markets"]:
                if market["key"] == "h2h":
                    outcomes = market["outcomes"]
                    odds_str = ", ".join([f"{o['name']}: {o['price']}" for o in outcomes])
                    st.write(f"Коефициенти: {odds_str}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
