import streamlit as st
import requests
from datetime import datetime

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
SPORT = "soccer"
REGION = "eu"
MARKETS = "h2h"

st.set_page_config(page_title="Стойностни Залози спрямо Pinnacle", layout="wide")
st.title("Стойностни залози чрез сравнение с Pinnacle")

# Изчисление на вероятности по наша логика
def calculate_probabilities(teams):
    return {"home": 0.40, "draw": 0.30, "away": 0.30}  # примерна логика

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
params = {
    "regions": REGION,
    "markets": MARKETS,
    "oddsFormat": "decimal",
    "apiKey": API_KEY
}

response = requests.get(url, params=params)
if response.status_code != 200:
    st.error(f"Грешка при зареждане: {response.status_code} {response.text}")
    st.stop()

data = response.json()
st.write(f"Общо заредени мачове: {len(data)}")

for match in data:
    teams = match.get("teams", [])
    commence_time = datetime.fromisoformat(match["commence_time"]).strftime("%Y-%m-%d %H:%M")
    bookmakers = match.get("bookmakers", [])

    pinnacle = next((b for b in bookmakers if b["key"] == "pinnacle"), None)
    if not pinnacle:
        continue

    pinnacle_market = next((m for m in pinnacle["markets"] if m["key"] == "h2h"), None)
    if not pinnacle_market:
        continue

    pinnacle_outcomes = {o["name"]: o["price"] for o in pinnacle_market["outcomes"]}

    for bookmaker in bookmakers:
        if bookmaker["key"] == "pinnacle":
            continue

        market = next((m for m in bookmaker["markets"] if m["key"] == "h2h"), None)
        if not market:
            continue

        for outcome in market["outcomes"]:
            name = outcome["name"]
            other_odds = outcome["price"]
            pinnacle_odds = pinnacle_outcomes.get(name)

            if pinnacle_odds and other_odds > pinnacle_odds:
                market_value = other_odds / pinnacle_odds

                if market_value > 1.20:
                    probs = calculate_probabilities(teams)
                    if name == teams[0]:  # home
                        prob = probs["home"]
                    elif name == teams[1]:  # away
                        prob = probs["away"]
                    else:
                        prob = probs["draw"]

                    custom_value = prob * other_odds

                    st.markdown("---")
                    st.subheader(f"{teams[0]} vs {teams[1]} ({commence_time})")
                    st.write(f"**Букмейкър:** {bookmaker['title']}")
                    st.write(f"**Пазар:** {name}")
                    st.write(f"**Коефициент в {bookmaker['key']}:** {other_odds}")
                    st.write(f"**Коефициент в Pinnacle:** {pinnacle_odds}")
                    st.write(f"**Отклонение (value):** {market_value:.2f}")
                    st.write(f"**Нашата оценка (value):** {custom_value:.2f}")
                    
