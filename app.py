import streamlit as st
import requests
from datetime import datetime
import pytz
from functools import lru_cache

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

# Позволени букмейкъри
ALLOWED_BOOKMAKERS = ["bet365", "pinnacle", "unibet", "williamhill"]

# Заглавие
st.title("Детектор на стойностни футболни залози")
st.write("Зареждане на мачове и анализ на коефициенти...")

# Филтриране на пазари по букмейкъри
def filter_markets_by_bookmaker(bookmakers):
    for bookmaker in bookmakers:
        if bookmaker.get("key") in ALLOWED_BOOKMAKERS:
            return bookmaker.get("markets", [])
    return []

# Кеширана функция за форма
@lru_cache(maxsize=128)
def get_team_form(team_name):
    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    r = requests.get(url, headers=headers)
    try:
        team_id = r.json()["response"][0]["team"]["id"]
        stats_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024&league=1"
        stats = requests.get(stats_url, headers=headers).json()
        form_str = stats.get("response", {}).get("form", "")
        if form_str:
            return form_str.count("W") / len(form_str)
    except:
        pass
    return 0.5  # ако няма данни

# Вероятности
def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)
    prob_home = round(0.4 + (form_home - form_away) * 0.3, 2)
    prob_away = round(0.4 + (form_away - form_home) * 0.3, 2)
    prob_draw = round(1 - prob_home - prob_away, 2)
    return max(min(prob_home, 0.85), 0.05), max(min(prob_draw, 0.85), 0.05), max(min(prob_away, 0.85), 0.05)

# Стойностен залог?
def is_value_bet(prob, odds):
    return prob * odds > 1.05

# Заявка към Odds API
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
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
    matches = requests.get(url, params=params).json()

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        start = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))
        st.subheader(f"{home} vs {away} ({start.strftime('%Y-%m-%d %H:%M')})")

        markets = filter_markets_by_bookmaker(match.get("bookmakers", []))
        prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

        for market in markets:
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    team = outcome["name"]
                    odds = outcome["price"]
                    prob = prob_home if team == home else prob_away if team == away else prob_draw
                    value = round(prob * odds, 2)
                    if is_value_bet(prob, odds):
                        st.markdown(f"**Стойностен залог (1X2):** {team} при {odds} (стойност: {value})")

            elif market["key"] == "totals":
                for outcome in market["outcomes"]:
                    if "2.5" in outcome.get("point", ""):
                        label = outcome["name"]
                        odds = outcome["price"]
                        prob = 0.6 if label.lower() == "over" else 0.4  # псевдо-оценка
                        value = round(prob * odds, 2)
                        if is_value_bet(prob, odds):
                            st.markdown(f"**Стойностен залог (Над/Под 2.5):** {label} при {odds} (стойност: {value})")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
