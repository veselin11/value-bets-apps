import streamlit as st
import requests
from datetime import datetime
import pytz

# Кеширане
team_form_cache = {}
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

ALLOWED_BOOKMAKERS = ["bet365", "unibet", "williamhill", "bwin", "betfair", "10bet"]

st.title("Стойностни залози (Pinnacle като база)")

# Вземане на форма
def get_team_form(team_name):
    if team_name in team_form_cache:
        return team_form_cache[team_name]
    try:
        url = f"https://v3.football.api-sports.io/teams?search={team_name}"
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        team_id = requests.get(url, headers=headers).json()['response'][0]['team']['id']

        stats_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024&league=1"
        stats = requests.get(stats_url, headers=headers).json()
        form_str = stats.get("response", {}).get("form", "")
        score = form_str.count("W") / len(form_str) if form_str else 0.5
    except:
        score = 0.5
    team_form_cache[team_name] = score
    return score

# Наш модел за вероятности
def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)
    prob_home = round(0.4 + (form_home - form_away) * 0.3, 2)
    prob_away = round(0.4 + (form_away - form_home) * 0.3, 2)
    prob_draw = round(1 - prob_home - prob_away, 2)
    return max(min(prob_home, 0.85), 0.05), max(min(prob_draw, 0.85), 0.05), max(min(prob_away, 0.85), 0.05)

# Заявка към Odds API
url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "apiKey": ODDS_API_KEY
}

try:
    res = requests.get(url, params=params)
    res.raise_for_status()
    matches = res.json()

    for match in matches:
        home = match['home_team']
        away = match['away_team']
        time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).astimezone(pytz.timezone("Europe/Sofia"))
        bookmakers = match.get("bookmakers", [])

        pinnacle = next((b for b in bookmakers if b['key'] == "pinnacle"), None)
        if not pinnacle:
            continue

        pinnacle_odds = {o['name']: o['price'] for o in pinnacle['markets'][0]['outcomes']}

        for bookmaker in bookmakers:
            if bookmaker['key'] not in ALLOWED_BOOKMAKERS:
                continue

            for outcome in bookmaker['markets'][0]['outcomes']:
                team = outcome['name']
                other_odds = outcome['price']
                pin_odds = pinnacle_odds.get(team)

                if not pin_odds:
                    continue

                market_value = (1 / pin_odds) * other_odds
                if market_value > 1.20:
                    prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

                    if team == home:
                        prob = prob_home
                    elif team == away:
                        prob = prob_away
                    else:
                        prob = prob_draw

                    custom_value = prob * other_odds

                    if custom_value > 1.05:
                        st.subheader(f"{home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
                        st.markdown(f"**Стойностен залог:** {team} при {bookmaker['key']} @ {other_odds} (value: {market_value:.2f}, model: {custom_value:.2f})")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
