import streamlit as st
import requests
from datetime import datetime
import pytz

# Кеширане
team_form_cache = {}
h2h_cache = {}

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

# Позволени букмейкъри
ALLOWED_BOOKMAKERS = ["bet365", "pinnacle", "unibet", "williamhill"]

st.title("Детектор на стойностни футболни залози")
st.write("Зареждане на мачове и коефициенти")

# Филтриране на маркетите само по позволени букмейкъри
def filter_markets_by_bookmaker(bookmakers):
    for bookmaker in bookmakers:
        if bookmaker.get('key') in ALLOWED_BOOKMAKERS:
            return bookmaker.get('markets', [])
    return []

# Вземане на форма
def get_team_form(team_name):
    if team_name in team_form_cache:
        return team_form_cache[team_name]

    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    try:
        team_id = data['response'][0]['team']['id']
        form_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024&league=1"
        form_response = requests.get(form_url, headers=headers)
        form_data = form_response.json()

        form_str = form_data.get("response", {}).get("form", "")
        if form_str:
            form_score = form_str.count("W") / len(form_str)
        else:
            form_score = 0.5
    except (IndexError, KeyError, TypeError):
        form_score = 0.5

    team_form_cache[team_name] = form_score
    return form_score

# Изчисляване на вероятности на база форма и H2H (псевдо)
def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)

    prob_home = round(0.4 + (form_home - form_away) * 0.3, 2)
    prob_away = round(0.4 + (form_away - form_home) * 0.3, 2)
    prob_draw = round(1 - prob_home - prob_away, 2)

    return max(min(prob_home, 0.85), 0.05), max(min(prob_draw, 0.85), 0.05), max(min(prob_away, 0.85), 0.05)

# Стойностен залог ли е?
def is_value_bet(prob, odds):
    return prob * odds > 1.05

# Заявка за мачове
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h,totals",
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

    for match in matches:
        home = match['home_team']
        away = match['away_team']
        commence = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).astimezone(pytz.timezone("Europe/Sofia"))
        st.subheader(f"{home} vs {away} ({commence.strftime('%Y-%m-%d %H:%M')})")

        markets = filter_markets_by_bookmaker(match.get("bookmakers", []))
        prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

        for market in markets:
            if market['key'] == 'h2h':
                outcomes = market['outcomes']
                for outcome in outcomes:
                    team = outcome['name']
                    odds = outcome['price']
                    if team == home:
                        prob = prob_home
                    elif team == away:
                        prob = prob_away
                    else:
                        prob = prob_draw

                    value = round(prob * odds, 2)
                    if is_value_bet(prob, odds):
                        st.markdown(f"**Стойностен залог:** {team} при коеф. {odds} (стойност: {value})")
except Exception as e:
    st.error(f"Грешка при зареждане на мачове: {e}")
