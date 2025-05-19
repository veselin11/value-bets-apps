import streamlit as st
import requests
import json
import os
from datetime import datetime

# Константи
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
ALLOWED_BOOKMAKERS = ["betfair", "pinnacle", "bet365", "williamhill"]
CACHE_FILE = "stats_cache.json"

# Зареждане на кеш
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        stats_cache = json.load(f)
else:
    stats_cache = {}

# Запазване на кеша
def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(stats_cache, f)

# Филтриране на пазарите по букмейкър
def filter_markets_by_bookmaker(bookmakers):
    markets = []
    for bookmaker in bookmakers:
        if bookmaker.get('key') in ALLOWED_BOOKMAKERS:
            markets.extend(bookmaker.get('markets', []))
    return markets

# Изчисление на базова вероятност
def estimate_probability(odds):
    if odds <= 1.01:
        return 0.0
    return round(1 / odds, 2)

# Проверка за стойностен залог
def is_value_bet(prob, odds, threshold=0.05):
    value = prob * odds - 1
    return value > threshold, round(value, 2)

# Старт на Streamlit
st.title("Детектор на стойностни футболни залози")

st.markdown("---")
st.subheader("Зареждане на мачове и коефициенти")

odds_url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h,totals",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 3,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(odds_url, params=params)
    response.raise_for_status()
    matches = response.json()

    if not matches:
        st.warning("Няма намерени мачове или няма налични пазари.")
    else:
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            commence = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
            time_str = commence.strftime('%Y-%m-%d %H:%M')

            st.markdown(f"### {home} vs {away} ({time_str})")

            bookmakers = match.get('bookmakers', [])
            markets = filter_markets_by_bookmaker(bookmakers)

            if not markets:
                st.write("❌ Пропуснат мач – няма налични пазари от избраните букмейкъри.")
                continue

            for market in markets:
                if market['key'] not in ['h2h', 'totals']:
                    continue

                for outcome in market['outcomes']:
                    name = outcome['name']
                    odds = outcome['price']
                    prob = estimate_probability(odds)
                    value_bet, value_score = is_value_bet(prob, odds)

                    if value_bet:
                        st.success(f"Стойностен залог: **{market['key']} – {name}** @ {odds} | Вероятност: {prob} | Стойност: {value_score}")

except requests.exceptions.RequestException as e:
    st.error(f"Грешка при зареждане на мачове: {e}")

# Записване на кешираните заявки
save_cache()
