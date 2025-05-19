# streamlit_app.py

import streamlit as st
import requests

st.set_page_config(page_title="Футболни Коефициенти", layout="wide")
st.title("Футболни мачове и коефициенти (The Odds API)")

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
SPORT_KEY = "soccer"
URL = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds"

params = {
    "regions": "eu",           # Евро букмейкъри
    "markets": "h2h",          # Краен изход
    "oddsFormat": "decimal",   # Десетични коефициенти
    "dateFormat": "iso",
    "apiKey": API_KEY
}

with st.spinner("Зареждане на мачове..."):
    try:
        response = requests.get(URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            st.warning("Няма намерени мачове.")
        else:
            for match in data:
                st.subheader(f"{match['home_team']} vs {match['away_team']}")
                st.caption(f"Начало: {match['commence_time']}")

                for bookmaker in match.get("bookmakers", []):
                    st.markdown(f"**Букмейкър: {bookmaker['title']}**")
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "h2h":
                            odds_data = {
                                outcome["name"]: outcome["price"]
                                for outcome in market.get("outcomes", [])
                            }
                            st.write(odds_data)
                st.markdown("---")

    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP грешка: {err}")
    except Exception as e:
        st.error(f"Неочаквана грешка: {e}")
