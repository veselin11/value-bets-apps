import streamlit as st
import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
BASE_URL = "https://api.the-odds-api.com/v4/sports/"

EUROPEAN_LEAGUES = {
    "soccer_epl": "English Premier League",
    "soccer_spain_la_liga": "La Liga",
    "soccer_italy_serie_a": "Serie A",
    "soccer_germany_bundesliga": "Bundesliga",
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_portugal_primeira_liga": "Primeira Liga",
    "soccer_netherlands_eredivisie": "Eredivisie",
}

def get_odds_for_sport(sport_key):
    url = f"{BASE_URL}{sport_key}/odds/?regions=eu&markets=h2h&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Грешка при зареждане на коефициенти: {response.status_code} - {response.text}")
        return []

st.title("Стойностни футболни залози – Европа")

all_matches = []

for sport_key, league_name in EUROPEAN_LEAGUES.items():
    matches = get_odds_for_sport(sport_key)
    if matches:
        for match in matches:
            bookmakers = match.get('bookmakers', [])
            if not bookmakers:
                continue
            # Взимаме първия букмейкър и пазара h2h
            h2h_market = None
            for bookmaker in bookmakers:
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        h2h_market = market
                        break
                if h2h_market:
                    break
            if not h2h_market:
                continue

            odds_h2h = []
            for outcome in h2h_market['outcomes']:
                odds_h2h.append(outcome['price'])

            # Примерна оценка на вероятности
            probs = [1/o if o > 0 else 0 for o in odds_h2h]
            s = sum(probs)
            norm_probs = [p/s for p in probs]

            # Проверка за стойностен залог
            value_bets = []
            for i, outcome in enumerate(h2h_market['outcomes']):
                if outcome['price'] > (1 / norm_probs[i]):
                    value_bets.append({
                        "outcome": outcome['name'],
                        "price": outcome['price'],
                        "probability": norm_probs[i]
                    })

            if value_bets:
                all_matches.append({
                    "league": league_name,
                    "commence_time": match['commence_time'],
                    "home_team": match['home_team'],
                    "away_team": match['away_team'],
                    "value_bets": value_bets
                })

st.write(f"Намерени стойностни залози в {len(all_matches)} мача:")

for m in all_matches:
    st.markdown(f"### {m['home_team']} - {m['away_team']} ({m['league']})")
    st.write(f"Начало: {m['commence_time']}")
    for bet in m['value_bets']:
        st.write(f"- Залог: **{bet['outcome']}**, Коефициент: {bet['price']}, Оценена вероятност: {bet['probability']:.2f}")
