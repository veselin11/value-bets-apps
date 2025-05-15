import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

# Конфигурация на API
API_KEY = "a3d6004cbbb4d16e86e2837c27e465d8"
SPORT = "soccer_epl"  # Пример: Английска Висша лига
REGIONS = "eu"
MARKETS = "h2h"
ODDS_FORMAT = "decimal"
DATE_FORMAT = "iso"

st.set_page_config(page_title="Стойностни залози", layout="wide")
st.title("Стойностни залози - Реални Пазари")

# Функция за извличане на коефициенти от OddsAPI
@st.cache_data(ttl=300)
def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT,
        "dateFormat": DATE_FORMAT
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, f"Грешка при API заявката: {response.status_code}"
    return response.json(), None

# Логика за извличане на стойностни залози (само за днес, над 5% value)
def extract_value_bets(data):
    bets = []
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime('%Y-%m-%d')

    for match in data:
        start_time = datetime.fromisoformat(match.get("commence_time").replace("Z", "+00:00"))
        if start_time.strftime('%Y-%m-%d') != today_str:
            continue  # Прескачаме мачове, които не са днес

        home = match.get("home_team")
        away = match.get("away_team")

        for bookmaker in match.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") != "h2h":
                    continue
                for outcome in market.get("outcomes", []):
                    team = outcome.get("name")
                    odds = outcome.get("price")
                    implied_prob = 1 / odds
                    fair_prob = 0.30  # Примерна оценка на вероятност
                    value = (fair_prob * odds - 1) * 100
                    if value >= 5:
                        bets.append({
                            "Мач": f"{home} vs {away}",
                            "Отбор": team,
                            "Коефициент": round(odds, 2),
                            "Старт": start_time.strftime('%Y-%m-%d %H:%M'),
                            "Букмейкър": bookmaker.get("title"),
                            "Value %": round(value, 2)
                        })
    return pd.DataFrame(bets)

# Основен поток
with st.spinner("Зареждане на днешните залози..."):
    data, error = get_odds()
    if error:
        st.error(error)
    elif data:
        df = extract_value_bets(data)
        if not df.empty:
            st.success(f"Открити {len(df)} стойностни залози за днес!")
            st.dataframe(df.sort_values(by="Value %", ascending=False), use_container_width=True)
        else:
            st.warning("Няма стойностни залози за днес.")
    else:
        st.warning("Няма налични данни от API.")
