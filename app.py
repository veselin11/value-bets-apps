import streamlit as st
import requests
from datetime import datetime
import pytz

# Въведи своя API ключ тук
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

st.title("Всички футболни мачове и коефициенти (h2h)")

url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 2
    ,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()
    
    if not matches:
        st.warning("Няма налични мачове в момента.")
    
    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))
        
        st.markdown(f"### {home} vs {away} — {time.strftime('%Y-%m-%d %H:%M')}")
        
        for bookmaker in match["bookmakers"]:
            st.markdown(f"**{bookmaker['title']}**")
            for market in bookmaker["markets"]:
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        st.write(f"{outcome['name']}: {outcome['price']}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
