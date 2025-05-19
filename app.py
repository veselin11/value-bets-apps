import streamlit as st
import requests
from datetime import datetime
import pytz
import time

# Кеширане за форма
team_form_cache = {}

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

# Позволени букмейкъри - с акцент върху Bet365
ALLOWED_BOOKMAKERS = ["bet365", "pinnacle", "unibet", "williamhill"]

st.title("Детектор на стойностни футболни залози с фокус Bet365")
st.write("Зареждане на мачове и коефициенти...")

# Функция за кеширане и вземане на форма от API-Football
def get_team_form(team_name):
    if team_name in team_form_cache:
        return team_form_cache[team_name]

    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        team_id = data['response'][0]['team']['id']

        form_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024&league=1"
        form_response = requests.get(form_url, headers=headers)
        form_data = form_response.json()

        form_str = form_data.get("response", {}).get("form", "")
        form_score = form_str.count("W") / len(form_str) if form_str else 0.5
    except Exception:
        form_score = 0.5

    team_form_cache[team_name] = form_score
    return form_score

# Вероятности базирани на форма
def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)

    prob_home = max(min(0.4 + (form_home - form_away) * 0.3, 0.85), 0.05)
    prob_away = max(min(0.4 + (form_away - form_home) * 0.3, 0.85), 0.05)
    prob_draw = max(min(1 - prob_home - prob_away, 0.85), 0.05)
    return round(prob_home, 2), round(prob_draw, 2), round(prob_away, 2)

# Стойностен залог
def is_value_bet(prob, odds):
    return prob * odds > 1.05

# Вземаме коефициенти на Bet365 и останалите
def get_bet365_and_others(markets):
    bet365_odds = {}
    other_odds = {}

    for bookmaker in markets:
        key = bookmaker.get('key')
        if key not in ALLOWED_BOOKMAKERS:
            continue

        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    team = outcome['name']
                    price = outcome['price']
                    if key == 'bet365':
                        bet365_odds[team] = price
                    else:
                        if team not in other_odds or price > other_odds[team]:
                            other_odds[team] = price
    return bet365_odds, other_odds

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

        bet365_odds, other_odds = get_bet365_and_others(match.get("bookmakers", []))

        if not bet365_odds:
            st.info("Bet365 не предоставя коефициенти за този мач.")
            continue

        prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

        # Проверка за стойностни залози само ако коефициентът на Bet365 е по-висок от останалите
        for team in bet365_odds:
            odds_bet365 = bet365_odds[team]
            odds_others = other_odds.get(team, 0)

            # Търсим случаи, където Bet365 дава по-висок коефициент
            if odds_bet365 > odds_others:
                # Определяме вероятност според отбора
                if team == home:
                    prob = prob_home
                elif team == away:
                    prob = prob_away
                else:
                    prob = prob_draw

                value = round(prob * odds_bet365, 2)
                if is_value_bet(prob, odds_bet365):
                    st.markdown(f"**Стойностен залог (Bet365 по-висок коеф.):** {team} при коеф. {odds_bet365} (стойност: {value})")
except Exception as e:
    st.error(f"Грешка при зареждане на мачове: {e}")
