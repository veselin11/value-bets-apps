import streamlit as st
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

st.title("Футболни залози - Анализ и Value Bets (Европа)")

# Функция за скрейпинг на последните 5 мача и резултати (W/D/L)
def get_last_matches_form(team_url):
    try:
        res = requests.get(team_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        form = []
        table = soup.find('table', id='results')
        if not table:
            return []
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells:
                result = cells[6].text.strip()
                if result in ['W', 'D', 'L']:
                    form.append(result)
            if len(form) == 5:
                break
        return form
    except:
        return []

# Примерни URL-та на отбори в Европа (Премиър Лийг)
teams = {
    "Liverpool": "https://fbref.com/en/squads/18bb7c10/Liverpool-Stats",
    "Manchester City": "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats",
    "Real Madrid": "https://fbref.com/en/squads/53a0f082/Real-Madrid-Stats",
    "Barcelona": "https://fbref.com/en/squads/206d90db/Barcelona-Stats",
    "Bayern Munich": "https://fbref.com/en/squads/b7a741f9/Bayern-Munich-Stats",
    "Juventus": "https://fbref.com/en/squads/4f9dcd71/Juventus-Stats",
}

st.sidebar.header("Избери отбори")
home_team = st.sidebar.selectbox("Домакин", list(teams.keys()))
away_team = st.sidebar.selectbox("Гост", list(teams.keys()), index=1)

if home_team == away_team:
    st.error("Моля, избери различни отбори.")
    st.stop()

st.write(f"### Форма на {home_team} (последни 5 мача)")
home_form = get_last_matches_form(teams[home_team])
st.write(home_form)

st.write(f"### Форма на {away_team} (последни 5 мача)")
away_form = get_last_matches_form(teams[away_team])
st.write(away_form)

# Проста точкова система за форма: W=3, D=1, L=0
def form_score(form):
    score_map = {'W':3, 'D':1, 'L':0}
    return sum(score_map.get(r,0) for r in form)

home_form_score = form_score(home_form)
away_form_score = form_score(away_form)

st.write(f"Форма точки - {home_team}: {home_form_score}, {away_team}: {away_form_score}")

# Въвеждане на реални коефициенти от потребителя
st.sidebar.header("Въведи коефициенти")
odd_home = st.sidebar.number_input("Коефициент за домакин", min_value=1.01, value=2.0)
odd_draw = st.sidebar.number_input("Коефициент за равен", min_value=1.01, value=3.5)
odd_away = st.sidebar.number_input("Коефициент за гост", min_value=1.01, value=3.0)

# Проста формула за вероятност от форма (тежест 0.5)
w_form = 0.5
# За демонстрация - нормализираме само форма
total = home_form_score + away_form_score + 1e-5
prob_home = (home_form_score / total) * w_form + (1 - w_form) / 3
prob_away = (away_form_score / total) * w_form + (1 - w_form) / 3
prob_draw = 1 - prob_home - prob_away
if prob_draw < 0:
    prob_draw = 0.1  # Корекция

st.write(f"Изчислени вероятности: Домакин: {prob_home:.2f}, Равен: {prob_draw:.2f}, Гост: {prob_away:.2f}")

# Изчисляване на value bets
value_home = odd_home * prob_home - 1
value_draw = odd_draw * prob_draw - 1
value_away = odd_away * prob_away - 1

st.write(f"Value bet за Домакин: {value_home:.3f}")
st.write(f"Value bet за Равен: {value_draw:.3f}")
st.write(f"Value bet за Гост: {value_away:.3f}")

# Банка и мениджмънт
st.sidebar.header("Управление на банка")
bankroll = st.sidebar.number_input("Текуща банка (лв.)", min_value=1.0, value=500.0)
risk_percent = st.sidebar.slider("Процент от банка за залог", min_value=1, max_value=10, value=3)

stake = bankroll * (risk_percent / 100)

st.write(f"Препоръчан залог: {stake:.2f} лв.")

# Препоръка за залог (само ако value bet > 0)
recommendation = []
if value_home > 0:
    recommendation.append(f"Залог: Домакин на {home_team} със стойност {value_home:.3f}")
if value_draw > 0:
    recommendation.append(f"Залог: Равен резултат със стойност {value_draw:.3f}")
if value_away > 0:
    recommendation.append(f"Залог: Гост на {away_team} със стойност {value_away:.3f}")

if recommendation:
    st.success("Препоръчани залози:")
    for r in recommendation:
        st.write(r)
else:
    st.info("Няма изгодни залози на база въведените коефициенти и форма.")

