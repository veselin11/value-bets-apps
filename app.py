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
    markets = "h2h,totals,bothteams"
    url = f"{BASE_URL}{sport_key}/odds/?regions=eu&markets={markets}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Грешка при зареждане на коефициенти: {response.status_code} - {response.text}")
        return []

def calc_probabilities(odds):
    """Нормализира вероятностите от коефициенти"""
    probs = [1/o if o > 0 else 0 for o in odds]
    s = sum(probs)
    return [p/s for p in probs] if s > 0 else []

def find_value_bets(outcomes):
    odds = [outcome['price'] for outcome in outcomes]
    probs = calc_probabilities(odds)
    value_bets = []
    for i, outcome in enumerate(outcomes):
        expected_value = outcome['price'] * probs[i]
        # Праг 1.05 за стойностен залог (EV > 1.05)
        if expected_value > 1.05:
            value_bets.append({
                "outcome": outcome['name'],
                "price": outcome['price'],
                "probability": probs[i],
                "expected_value": expected_value
            })
    return value_bets

st.title("Стойностни футболни залози – Европа")

all_matches = []

for sport_key, league_name in EUROPEAN_LEAGUES.items():
    matches = get_odds_for_sport(sport_key)
    st.write(f"Лига: {league_name}, Мачове: {len(matches)}")
    for match in matches:
        bookmakers = match.get('bookmakers', [])
        if not bookmakers:
            continue

        # За всеки мач вземаме първия букмейкър с пазарите
        bookmaker = bookmakers[0]

        # Събираме стойностни залози за различни пазари
        match_value_bets = []

        for market in bookmaker.get('markets', []):
            key = market['key']
            outcomes = market.get('outcomes', [])
            if not outcomes:
                continue

            value_bets = find_value_bets(outcomes)
            if value_bets:
                match_value_bets.append({
                    "market": key,
                    "value_bets": value_bets
                })

        if match_value_bets:
            all_matches.append({
                "league": league_name,
                "commence_time": match['commence_time'],
                "home_team": match['home_team'],
                "away_team": match['away_team'],
                "value_bets_by_market": match_value_bets
            })

st.write(f"Намерени стойностни залози в {len(all_matches)} мача:")

for m in all_matches:
    st.markdown(f"### {m['home_team']} - {m['away_team']} ({m['league']})")
    st.write(f"Начало: {m['commence_time']}")
    for market_bets in m['value_bets_by_market']:
        market_name = market_bets['market']
        st.write(f"Пазар: **{market_name}**")
        for bet in market_bets['value_bets']:
            st.write(f"- Залог: **{bet['outcome']}**, Коефициент: {bet['price']}, Оценена вероятност: {bet['probability']:.2f}, Очаквана стойност: {bet['expected_value']:.2f}")
