import streamlit as st
import requests
import pandas as pd
import numpy as np
from scipy.stats import poisson
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
from functools import lru_cache

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
    # Добави още отбори при нужда
}

# ================== API ФУНКЦИИ ================== #
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
        st.warning(f"Отборът {team_name} не е в TEAM_ID_MAPPING")
        return None
    
    try:
        response = requests.get(
            f"https://api.football-data.org/v4/teams/{team_id}/matches",
            headers={"X-Auth-Token": FOOTBALL_DATA_API_KEY},
            params={"status": "FINISHED", "limit": 10}
        )
        response.raise_for_status()
        return response.json()["matches"]
    except Exception as e:
        st.error(f"Грешка при взимане на статистики за {team_name}: {str(e)}")
        return None

# ================== АНАЛИТИЧНИ ФУНКЦИИ ================== #
def calculate_poisson_probabilities(home_avg, away_avg):
    home_win, draw, away_win = 0, 0, 0
    for i in range(0, 6):
        for j in range(0, 6):
            p = poisson.pmf(i, home_avg) * poisson.pmf(j, away_avg)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    return home_win, draw, away_win

def calculate_value_bets(probabilities, odds):
    value = {}
    for outcome in ['home', 'draw', 'away']:
        implied_prob = 1 / odds[outcome]
        value[outcome] = probabilities[outcome] - implied_prob
    return value

# ================== МАШИННО ОБУЧЕНИЕ ================== #
def predict_with_ai(home_stats, away_stats):
    try:
        model = joblib.load("model.pkl")
        scaler = joblib.load("scaler.pkl")
        features = np.array([
            home_stats["avg_goals"],
            away_stats["avg_goals"],
            home_stats["win_rate"],
            away_stats["win_rate"]
        ]).reshape(1, -1)
        scaled_features = scaler.transform(features)
        prediction = model.predict_proba(scaled_features)
        return prediction[0]
    except Exception as e:
        st.error(f"Грешка при AI прогноза: {str(e)}")
        return None

# ================== UI ================== #
def main():
    st.set_page_config(page_title="Advanced Bet Analyzer", layout="wide", page_icon="⚽")
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

    # ==== Подобрена обработка на статистики ==== #
    # HOME
    if home_stats_raw and len(home_stats_raw) > 0:
        last_home_matches = home_stats_raw[-10:]
        home_goals = [m["score"]["fullTime"]["home"] for m in last_home_matches if m["score"]["fullTime"]["home"] is not None]
        home_wins = [1 if m["score"]["fullTime"]["home"] > m["score"]["fullTime"]["away"] else 0 for m in last_home_matches]
        home_avg_goals = np.mean(home_goals) if home_goals else 1.2
        home_win_rate = np.mean(home_wins) if home_wins else 0.5
    else:
        home_avg_goals = 1.2
        home_win_rate = 0.5

    home_stats = {
        "avg_goals": home_avg_goals,
        "win_rate": home_win_rate
    }

    # AWAY
    if away_stats_raw and len(away_stats_raw) > 0:
        last_away_matches = away_stats_raw[-10:]
        away_goals = [m["score"]["fullTime"]["away"] for m in last_away_matches if m["score"]["fullTime"]["away"] is not None]
        away_wins = [1 if m["score"]["fullTime"]["away"] > m["score"]["fullTime"]["home"] else 0 for m in last_away_matches]
        away_avg_goals = np.mean(away_goals) if away_goals else 0.9
        away_win_rate = np.mean(away_wins) if away_wins else 0.3
    else:
        away_avg_goals = 0.9
        away_win_rate = 0.3

    away_stats = {
        "avg_goals": away_avg_goals,
        "win_rate": away_win_rate
    }

    # Вероятности
    prob_home, prob_draw, prob_away = calculate_poisson_probabilities(
        home_stats["avg_goals"],
        away_stats["avg_goals"]
    )

    # Коефициенти
    best_odds = {
        "home": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == match["home_team"]),
        "draw": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == "Draw"),
        "away": max(o["price"] for b in match["bookmakers"] for o in b["markets"][0]["outcomes"] if o["name"] == match["away_team"])
    }

    # Value Bets
    value_bets = calculate_value_bets(
        {"home": prob_home, "draw": prob_draw, "away": prob_away},
        best_odds
    )

    # ==== UI Tabs ==== #
    tab1, tab2, tab3 = st.tabs(["Основен анализ", "Разширена статистика", "AI Прогнози"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(f"🏠 {match['home_team']}")
            st.metric("Средни голове", f"{home_stats['avg_goals']:.2f}")
            st.metric("Шанс за победа", f"{prob_home*100:.1f}%")
            st.metric("Value Score", f"{value_bets['home']*100:.1f}%", delta="Стойностен" if value_bets['home'] > 0 else "Нестойностен")

        with col2:
            st.subheader("⚖ Равен")
            st.metric("Шанс", f"{prob_draw*100:.1f}%")
            st.metric("Value Score", f"{value_bets['draw']*100:.1f}%", delta="Стойностен" if value_bets['draw'] > 0 else "Нестойностен")

        with col3:
            st.subheader(f"✈ {match['away_team']}")
            st.metric("Средни голове", f"{away_stats['avg_goals']:.2f}")
            st.metric("Шанс за победа", f"{prob_away*100:.1f}%")
            st.metric("Value Score", f"{value_bets['away']*100:.1f}%", delta="Стойностен" if value_bets['away'] > 0 else "Нестойностен")

    with tab2:
        st.subheader("📈 Исторически показатели")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Последни 5 мача {match['home_team']}:**")
            for m in home_stats_raw[-5:] if home_stats_raw else []:
                result = f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"
                st.write(f"- {result} ({m['utcDate'][:10]})")

        with col2:
            st.write(f"**Последни 5 мача {match['away_team']}:**")
            for m in away_stats_raw[-5:] if away_stats_raw else []:
                result = f"{m['score']['fullTime']['away']}-{m['score']['fullTime']['home']}"
                st.write(f"- {result} ({m['utcDate'][:10]})")

    with tab3:
        st.subheader("🤖 AI Прогноза")
        if st.button("Генерирай прогноза"):
            ai_prediction = predict_with_ai(home_stats, away_stats)
            if ai_prediction is not None:
                st.write("### Вероятности:")
                st.write(f"- Победа {match['home_team']}: {ai_prediction[0]*100:.1f}%")
                st.write(f"- Равен: {ai_prediction[1]*100:.1f}%")
                st.write(f"- Победа {match['away_team']}: {ai_prediction[2]*100:.1f}%")

if __name__ == "__main__":
    main()
