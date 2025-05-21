import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
import joblib

# ================== КОНФИГУРАЦИЯ ================== #
FOOTBALL_DATA_API_KEY = st.secrets["FOOTBALL_DATA_API_KEY"]
ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
SPORT = "soccer_epl"

TEAM_ID_MAPPING = {
    "Manchester City": 65,
    "AFC Bournemouth": 1044,
    "Liverpool": 64,
    "Everton": 62,
    "Arsenal": 57,
    "Tottenham Hotspur": 73,
    # ... добавете останалите отбори
}

@st.cache_data(ttl=3600)
def get_live_odds():
    try:
        response = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Грешка при взимане на коефициенти: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_team_stats(team_name):
    team_id = TEAM_ID_MAPPING.get(team_name)
    if not team_id:
        st.warning(f"Не е намерен ID за отбор: {team_name}")
        return None
    
    try:
        response = requests.get(
            f"https://api.football-data.org/v4/teams/{team_id}/matches",
            headers={"X-Auth-Token": FOOTBALL_DATA_API_KEY},
            params={"status": "FINISHED", "limit": 5}
        )
        response.raise_for_status()
        data = response.json()
        if "matches" not in data or len(data["matches"]) == 0:
            st.warning(f"Няма завършени мачове за {team_name}")
            return None
        return data["matches"]
    except Exception as e:
        st.error(f"Грешка при взимане на статистики за {team_name}: {str(e)}")
        return None

def calculate_poisson_probabilities(home_avg, away_avg):
    home_win, draw, away_win = 0, 0, 0
    for i in range(6):
        for j in range(6):
            p = poisson.pmf(i, home_avg) * poisson.pmf(j, away_avg)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    return home_win, draw, away_win

def calculate_value_bets(probabilities, odds):
    value = {}
    for outcome in ['home', 'draw', 'away']:
        if odds.get(outcome) and odds[outcome] > 0:
            implied_prob = 1 / odds[outcome]
            value[outcome] = probabilities[outcome] - implied_prob
        else:
            value[outcome] = None  # няма валиден коефициент
    return value

def main():
    st.title("🔮 Advanced Bet Analyzer")

    matches = get_live_odds()
    if not matches:
        st.warning("Няма налични мачове в момента")
        return

    selected_match = st.selectbox(
        "Избери мач за анализ:",
        [f'{m["home_team"]} vs {m["away_team"]}' for m in matches]
    )
    match = next(m for m in matches if f'{m["home_team"]} vs {m["away_team"]}' == selected_match)

    home_stats_raw = get_team_stats(match["home_team"])
    away_stats_raw = get_team_stats(match["away_team"])

    if home_stats_raw:
        home_avg_goals = np.mean([m["score"]["fullTime"]["home"] for m in home_stats_raw])
        home_win_rate = np.mean([1 if m["score"]["fullTime"]["home"] > m["score"]["fullTime"]["away"] else 0 for m in home_stats_raw])
    else:
        st.warning(f"Липсва статистика за {match['home_team']}, използват се фиктивни стойности")
        home_avg_goals, home_win_rate = 1.2, 0.5

    if away_stats_raw:
        away_avg_goals = np.mean([m["score"]["fullTime"]["away"] for m in away_stats_raw])
        away_win_rate = np.mean([1 if m["score"]["fullTime"]["away"] > m["score"]["fullTime"]["home"] else 0 for m in away_stats_raw])
    else:
        st.warning(f"Липсва статистика за {match['away_team']}, използват се фиктивни стойности")
        away_avg_goals, away_win_rate = 0.9, 0.3

    prob_home, prob_draw, prob_away = calculate_poisson_probabilities(home_avg_goals, away_avg_goals)

    # Събиране на коефициенти с проверки
    try:
        best_odds = {
            "home": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == match["home_team"]),
            "draw": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == "Draw"),
            "away": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == match["away_team"]),
        }
    except Exception:
        st.warning("Не бяха намерени коефициенти за всички пазари.")
        best_odds = {"home": None, "draw": None, "away": None}

    value_bets = calculate_value_bets({"home": prob_home, "draw": prob_draw, "away": prob_away}, best_odds)

    st.write(f"### Анализ на мача: {selected_match}")
    st.write(f"- Вероятност за победа на домакин: {prob_home:.2%}")
    st.write(f"- Вероятност за равен: {prob_draw:.2%}")
    st.write(f"- Вероятност за победа на гост: {prob_away:.2%}")
    st.write(f"- Коефициенти: {best_odds}")
    st.write(f"- Value bets: {value_bets}")

if __name__ == "__main__":
    main()
