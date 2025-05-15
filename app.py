import streamlit as st
import requests
import pandas as pd

# Настройки
API_KEY = "a3d6004cbbb4d16e86e2837c27e465d8"
REGION = "eu"  # Европа
MARKET = "h2h"  # Победа/Равенство/Загуба

# Функция за изчисление на value %
def calculate_value(odds, implied_prob):
    return (odds * implied_prob - 1) * 100

# Заглавие
st.title("Value Залози - Футбол (Live & Prematch)")

# Извличане на данни
with st.spinner("Зареждане на прогнози..."):
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        rows = []
        for match in data:
            teams = match['home_team'] + " vs " + match['away_team']
            time = match['commence_time']
            for bookmaker in match['bookmakers']:
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        for outcome in outcomes:
                            team = outcome['name']
                            odds = outcome['price']
                            implied_prob = 1 / odds
                            value = calculate_value(odds, implied_prob)
                            if value > 5:
                                rows.append({
                                    "Мач": teams,
                                    "Отбор": team,
                                    "Коефициент": odds,
                                    "Value %": round(value, 2),
                                    "Час": time,
                                    "Букмейкър": bookmaker['title']
                                })

        if rows:
            df = pd.DataFrame(rows)
            df = df.sort_values(by="Value %", ascending=False).head(5)
            st.success("Намерени стойностни прогнози:")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Няма стойностни прогнози в момента.")
    else:
        st.error(f"Грешка при заявката: {response.status_code}")
        try:
            st.code(response.json())
        except:
            st.text(response.text)
