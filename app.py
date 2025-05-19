import streamlit as st
import requests
from datetime import datetime
import pytz

# Кеширане
team_form_cache = {}

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

# Позволени букмейкъри
ALLOWED_BOOKMAKERS = ["pinnacle", "bet365", "unibet", "williamhill"]

st.title("Детектор на стойностни футболни залози с Pinnacle")

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
        if form_str:
            form_score = form_str.count("W") / len(form_str)
        else:
            form_score = 0.5
    except Exception:
        form_score = 0.5

    team_form_cache[team_name] = form_score
    return form_score

def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)

    # Надграждане на оценката с форма и фиксиран баланс
    base_prob = 0.33
    prob_home = round(base_prob + (form_home - form_away) * 0.25, 3)
    prob_away = round(base_prob + (form_away - form_home) * 0.25, 3)
    prob_draw = round(1 - prob_home - prob_away, 3)

    # Ограничаване в интервал [0.05, 0.85]
    prob_home = min(max(prob_home, 0.05), 0.85)
    prob_away = min(max(prob_away, 0.05), 0.85)
    prob_draw = min(max(prob_draw, 0.05), 0.85)

    return prob_home, prob_draw, prob_away

def filter_bookmakers(bookmakers):
    return [b for b in bookmakers if b.get('key') in ALLOWED_BOOKMAKERS]

def get_odds_for_bookmaker(event, bookmaker_key):
    for bookmaker in event.get("bookmakers", []):
        if bookmaker.get("key") == bookmaker_key:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    odds = {}
                    for outcome in market.get("outcomes", []):
                        if outcome["name"] == event['home_team']:
                            odds['home'] = outcome["price"]
                        elif outcome["name"] == event['away_team']:
                            odds['away'] = outcome["price"]
                        else:
                            odds['draw'] = outcome["price"]
                    return odds
    return {}

def get_odds_excluding_bookmaker(event, exclude_key):
    odds_list = []
    for bookmaker in event.get("bookmakers", []):
        if bookmaker.get("key") != exclude_key:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    odds = {}
                    for outcome in market.get("outcomes", []):
                        if outcome["name"] == event['home_team']:
                            odds['home'] = outcome["price"]
                        elif outcome["name"] == event['away_team']:
                            odds['away'] = outcome["price"]
                        else:
                            odds['draw'] = outcome["price"]
                    odds_list.append(odds)
    return odds_list

def evaluate_value_bets(events):
    value_bets = []
    for event in events:
        home = event['home_team']
        away = event['away_team']

        pinnacle_odds = get_odds_for_bookmaker(event, "pinnacle")
        if not pinnacle_odds:
            continue

        other_odds_list = get_odds_excluding_bookmaker(event, "pinnacle")
        if not other_odds_list:
            continue

        prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

        for outcome_key, outcome_name in [('home', home), ('draw', 'Равен'), ('away', away)]:
            pinnacle_odd = pinnacle_odds.get(outcome_key)
            if pinnacle_odd is None:
                continue

            max_other_odd = max([odds.get(outcome_key, 0) for odds in other_odds_list], default=0)
            diff = pinnacle_odd - max_other_odd

            # Проверяваме дали коефициентът на Pinnacle е по-висок с разлика > 0
            if diff > 0:
                implied_prob = 1 / pinnacle_odd if pinnacle_odd else 0
                model_prob = {'home': prob_home, 'draw': prob_draw, 'away': prob_away}[outcome_key]
                value = round(model_prob / implied_prob, 2) if implied_prob else 0

                # Стойностен залог ако value > 1.20
                if value > 1.20:
                    value_bets.append({
                        "match": f"{home} vs {away}",
                        "outcome": outcome_name,
                        "pinnacle_odd": pinnacle_odd,
                        "max_other_odd": max_other_odd,
                        "difference": round(diff, 2),
                        "model_prob": round(model_prob, 3),
                        "implied_prob": round(implied_prob, 3),
                        "value": value
                    })
    # Сортираме по стойност (value) - най-висока първо
    value_bets.sort(key=lambda x: x["value"], reverse=True)
    return value_bets

def colorize_value(value):
    if value > 1.5:
        return "color: green; font-weight: bold"
    elif value > 1.3:
        return "color: darkgreen"
    elif value > 1.2:
        return "color: orange"
    else:
        return ""

# Основен код

st.write("Зареждане на мачове и анализ...")

url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 2,
    "apiKey": ODDS_API_KEY,
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()

    value_bets = evaluate_value_bets(matches)

    st.write(f"Общо заредени мачове: {len(matches)}")
    st.write(f"Намерени стойностни залози: {len(value_bets)}")

    for bet in value_bets:
        diff_color = "green" if bet["difference"] > 0.1 else "orange"
        st.markdown(f"### {bet['match']}")
        st.markdown(f"**{bet['outcome']}** при Pinnacle: {bet['pinnacle_odd']} | Макс. друг коеф.: {bet['max_other_odd']} | Разлика: "
                    f"<span style='color:{diff_color}'>{bet['difference']}</span>", unsafe_allow_html=True)
        st.markdown(f"→ Вероятност (модел): {bet['model_prob']} | Имплицитна вероятност: {bet['implied_prob']} | Стойност: "
                    f"<span style='{colorize_value(bet['value'])}'>{bet['value']}</span>", unsafe_allow_html=True)

        if bet["value"] > 1.20:
            st.markdown("→ **Стойностен залог!**")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
