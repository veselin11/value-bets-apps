import streamlit as st
import requests
from datetime import datetime
from functools import lru_cache

# Конфигурация
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"
HEADERS_API_FOOTBALL = {"x-apisports-key": API_FOOTBALL_KEY}

ALLOWED_BOOKMAKERS = ["betfair", "pinnacle", "marathonbet", "unibet_eu"]

st.title("Детектор на стойностни футболни залози")
st.write("Зареждане на мачове и коефициенти")

# Зареждане на мачове от Odds API
odds_url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h,totals",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 3,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(odds_url, params=params)
    response.raise_for_status()
    matches = response.json()

    if not matches:
        st.warning("Няма налични мачове.")

    def kelly_criterion(prob, odds, bankroll):
        edge = (prob * (odds - 1)) - (1 - prob)
        fraction = edge / (odds - 1) if odds > 1 else 0
        return max(0, bankroll * fraction)

    def calc_probabilities(home_form, away_form, h2h):
        prob_home = (home_form + h2h[0]) / 2
        prob_draw = h2h[1]
        prob_away = (away_form + h2h[2]) / 2
        total = prob_home + prob_draw + prob_away
        return prob_home / total, prob_draw / total, prob_away / total

    @lru_cache(maxsize=1000)
    def get_team_form(team):
        url = f"https://v3.football.api-sports.io/teams/statistics?team={team}&season=2024&league=39"
        r = requests.get(url, headers=HEADERS_API_FOOTBALL)
        if r.status_code == 200:
            data = r.json()
            return data['form'].count("W") / len(data['form']) if data['form'] else 0.5
        return 0.5

    @lru_cache(maxsize=1000)
    def get_h2h(home, away):
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home}-{away}"
        r = requests.get(url, headers=HEADERS_API_FOOTBALL)
        if r.status_code == 200:
            matches = r.json().get('response', [])
            h = sum(1 for m in matches if m['teams']['home']['winner'])
            d = sum(1 for m in matches if m['teams']['home']['draw'])
            a = sum(1 for m in matches if m['teams']['away']['winner'])
            total = h + d + a
            return (h / total, d / total, a / total) if total else (0.4, 0.2, 0.4)
        return (0.4, 0.2, 0.4)

    def filter_markets_by_bookmaker(markets):
        return [m for m in markets if m.get('bookmaker_key') in ALLOWED_BOOKMAKERS]

    for match in matches:
        home = match['home_team']
        away = match['away_team']
        time = datetime.fromisoformat(match['commence_time'].replace("Z", "+00:00"))
        st.subheader(f"{home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")

        home_form = get_team_form(home)
        away_form = get_team_form(away)
        h2h = get_h2h(home, away)

        prob_home, prob_draw, prob_away = calc_probabilities(home_form, away_form, h2h)

        st.write(f"**Вероятности (по форма и H2H):**")
        st.write(f"- Победа за {home}: {prob_home * 100:.1f}%")
        st.write(f"- Равен: {prob_draw * 100:.1f}%")
        st.write(f"- Победа за {away}: {prob_away * 100:.1f}%")

        markets = filter_markets_by_bookmaker(match.get('bookmakers', []))
        for market in markets:
            st.subheader(f"{market['key'].upper()} – {market['bookmaker']}")
            for outcome in market['outcomes']:
                name = outcome['name']
                price = outcome['price']

                if market['key'] == 'h2h':
                    if name == home:
                        prob = prob_home
                    elif name == away:
                        prob = prob_away
                    else:
                        prob = prob_draw
                elif market['key'] == 'totals':
                    prob = 0.55 if "Over" in name else 0.45

                fair_odds = 1 / prob if prob > 0 else None
                value = (price - fair_odds) / fair_odds if fair_odds else 0

                if fair_odds:
                    st.write(f"{name} @ {price:.2f} | Стойност: {value*100:.1f}% | Очакв. вероятност: {prob*100:.1f}%")

                    if value > 0.10:
                        stake = kelly_criterion(prob, price, bankroll=500)
                        st.success(f"**СТОЙНОСТЕН ЗАЛОГ:** {name} @ {price:.2f} | Преп. залог: {stake:.2f} лв.")

except requests.RequestException as e:
    st.error(f"Грешка при зареждане: {e}")
    
