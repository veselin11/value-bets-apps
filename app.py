import streamlit as st
import requests
import pandas as pd
import datetime

# Конфигурация
API_KEY = "e004e3601abd4b108a653f9f3a8c5ede"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

BANKROLL = 500  # Начална банка
VALUE_THRESHOLD = 0.03  # Минимална стойност за value bet
MARKET = "1X2"

# Функция за зареждане на активни лиги
@st.cache_data
def get_active_leagues():
    response = requests.get(f"{BASE_URL}/leagues", headers=HEADERS)
    data = response.json()
    leagues = [
        {"id": league["league"]["id"], "name": league["league"]["name"], "country": league["country"]["name"]}
        for league in data["response"]
        if league["league"]["type"] == "League" and league["seasons"][-1]["coverage"]["fixtures"]["events"]
    ]
    return leagues

# Функция за зареждане на мачове за днес
def get_today_fixtures(leagues):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    fixtures = []
    for league in leagues:
        response = requests.get(f"{BASE_URL}/fixtures?league={league['id']}&date={today}", headers=HEADERS)
        if response.status_code == 200:
            fixtures += response.json()["response"]
    return fixtures

# Форма на отбор за последните 5 мача
def get_team_form(team_id):
    response = requests.get(f"{BASE_URL}/teams/statistics?team={team_id}&season=2024", headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["form"]
    return ""

# Логика за оценка на вероятност
def estimate_win_probability(form_home, form_away):
    score = lambda form: sum([3 if x == 'W' else 1 if x == 'D' else 0 for x in form[-5:]])
    s_home = score(form_home)
    s_away = score(form_away)
    total = s_home + s_away + 1e-5
    return s_home / total, s_away / total

# Основен анализ
def run_analysis():
    leagues = get_active_leagues()
    fixtures = get_today_fixtures(leagues)
    results = []

    for match in fixtures:
        home = match["teams"]["home"]
        away = match["teams"]["away"]
        home_form = get_team_form(home["id"])
        away_form = get_team_form(away["id"])
        if len(home_form) < 5 or len(away_form) < 5:
            continue

        prob_home, prob_away = estimate_win_probability(home_form, away_form)

        # Временно зададени коефициенти (примерно 1.80 за домакин)
        odds_home = 1.80
        implied_prob_home = 1 / odds_home

        value = prob_home - implied_prob_home
        if value > VALUE_THRESHOLD:
            stake = BANKROLL * 0.05
            results.append({
                "Мач": f"{home['name']} vs {away['name']}",
                "Избор": home['name'],
                "Коефициент": odds_home,
                "Шанс": round(prob_home * 100, 1),
                "Стойност": round(value * 100, 2),
                "Залог": round(stake, 2)
            })

    return results

# Streamlit UI
st.title("Стойностни футболни залози (1X2) с реална статистика")
data = run_analysis()
st.write(f"Намерени срещи: {len(data)}")

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.info("Няма стойностни залози в момента.")
