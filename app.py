import streamlit as st
import requests
from datetime import datetime

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

# Заглавие
st.title("Детектор на стойностни футболни залози с форма и H2H")

HEADERS_FOOTBALL = {
    'x-apisports-key': API_FOOTBALL_KEY
}

def get_football_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "apiKey": ODDS_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_team_id(team_name, league_id=39, season=2023):
    url = f"https://v3.football.api-sports.io/teams?league={league_id}&season={season}&search={team_name}"
    resp = requests.get(url, headers=HEADERS_FOOTBALL)
    data = resp.json()
    if data['results'] > 0:
        return data['response'][0]['team']['id']
    return None

def get_last_matches(team_id, league_id=39, season=2023, last=5):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&league={league_id}&season={season}&last={last}"
    resp = requests.get(url, headers=HEADERS_FOOTBALL)
    data = resp.json()
    return data['response']

def get_h2h_matches(team1_id, team2_id, last=5):
    url = f"https://v3.football.api-sports.io/fixtures?h2h={team1_id}-{team2_id}&last={last}"
    resp = requests.get(url, headers=HEADERS_FOOTBALL)
    data = resp.json()
    return data['response']

def calculate_form_prob(team_id, league_id=39, season=2023):
    matches = get_last_matches(team_id, league_id, season)
    if not matches:
        return 0.33  # При липса на данни - равен шанс

    points = 0
    total = 0
    for m in matches:
        if m['teams']['home']['id'] == team_id:
            score_for = m['goals']['home']
            score_against = m['goals']['away']
        else:
            score_for = m['goals']['away']
            score_against = m['goals']['home']

        if score_for > score_against:
            points += 3
        elif score_for == score_against:
            points += 1
        total += 3

    return points / total if total > 0 else 0.33

def estimate_match_prob(home_id, away_id):
    home_form = calculate_form_prob(home_id)
    away_form = calculate_form_prob(away_id)
    total = home_form + away_form
    if total == 0:
        return 0.33, 0.33, 0.33
    p_home = home_form / total
    p_away = away_form / total
    p_draw = 1 - (p_home + p_away)
    return p_home, p_draw, p_away

# Приложение
try:
    odds_data = get_football_odds()
except Exception as e:
    st.error(f"Грешка при зареждане на коефициенти: {e}")
    st.stop()

matches = odds_data
if not matches:
    st.write("Няма налични мачове.")
    st.stop()

for match in matches[:10]:  # показваме първите 10 мача
    home = match['home_team']
    away = match['away_team']
    commence_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
    st.write(f"### {home} vs {away} - {commence_time.strftime('%Y-%m-%d %H:%M')}")

    # Взимаме ID-тата на отборите
    league_id = match['sport_key']  # Тук трябва да се мапне към api-football лига - важно да уточним
    season = 2023

    home_id = get_team_id(home, league_id=39, season=season)  # за проба взимаме Висша лига (39)
    away_id = get_team_id(away, league_id=39, season=season)

    if home_id and away_id:
        p_home, p_draw, p_away = estimate_match_prob(home_id, away_id)
        st.write(f"Вероятности според форма: Домакин {p_home:.2f}, Равенство {p_draw:.2f}, Гост {p_away:.2f}")
    else:
        st.write("Няма достатъчно статистика за изчисляване на вероятности.")

    # Букмейкърски коефициенти за х2х
    for bookmaker in match.get('bookmakers', []):
        st.write(f"Букмейкър: {bookmaker['title']}")
        for market in bookmaker['markets']:
            if market['key'] == 'h2h':
                outcomes = market['outcomes']
                for outcome in outcomes:
                    st.write(f" - {outcome['name']}: {outcome['price']}")

    st.write("---")
