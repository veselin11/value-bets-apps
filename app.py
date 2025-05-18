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
    # Добави още, ако искаш
}

MARKETS_TO_CHECK = ["h2h", "totals", "bothteams"]

def get_odds_for_sport(sport_key):
    url = f"{BASE_URL}{sport_key}/odds/?regions=eu&markets=h2h,totals,bothteams&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Грешка при зареждане на коефициенти: {response.status_code}")
        return []

def is_value_bet(bookmaker_odds, my_prob):
    # Стойностна залог, ако коефициент > 1 / вероятност
    return bookmaker_odds > (1 / my_prob)

def estimate_probabilities(odds_h2h):
    # Тук може да сложиш сложна формула, за сега използвам имплицитната вероятност нормализирана
    probs = [1/o if o > 0 else 0 for o in odds_h2h]
    s = sum(probs)
    norm_probs = [p/s for p in probs]
    return norm_probs  # [prob_home, prob_draw, prob_away]

st.title("Стойностни футболни залози – Европа")

all_matches = []

for sport_key, league_name in EUROPEAN_LEAGUES.items():
    matches = get_odds_for_sport(sport_key)
    if matches:
        for match in matches:
            # Проверка дали са нужните пазари
            markets = {m['key']: m for m in match.get('bookmakers', [])[0].get('markets', [])} if match.get('bookmakers') else {}
            if not markets:
                continue

            # Вземаме 1X2 (h2h) пазар
            h2h_market = None
            totals_market = None
            bothteams_market = None

            for bookmaker in match.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        h2h_market = market
                    elif market['key'] == 'totals':
                        totals_market = market
                    elif market['key'] == 'bothteams':
                        bothteams_market = market

            if not h2h_market:
                continue

            # Вземаме коефициенти за 1X2
            odds_h2h = []
            for outcome in h2h_market['outcomes']:
                odds_h2h.append(outcome['price'])

            probs = estimate_probabilities(odds_h2h)

            # Проверка за value bet - за всеки резултат
            value_bets = []
            for i, outcome in enumerate(h2h_market['outcomes']):
                if is_value_bet(outcome['price'], probs[i]):
                    value_bets.append({
                        "outcome": outcome['name'],
                        "price": outcome['price'],
                        "probability": probs[i]
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

