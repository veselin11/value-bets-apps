import requests
import streamlit as st
from datetime import datetime

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"

# Статични оценки на вероятност (примерни, може да се подобрят допълнително)
def estimate_probability(team: str, opponent: str) -> float:
    # Примерна вероятност на база име (за реална оценка да се използва H2H, форма и класиране)
    return 0.40  # Засега фиксирана, ще се подобри по-късно със статистика

def calculate_value(odd: float, probability: float) -> float:
    return odd * probability

st.title("Стойностни залози чрез сравнение с Pinnacle")

params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "apiKey": API_KEY,
    "daysFrom": 0,
    "daysTo": 2
}

response = requests.get(BASE_URL, params=params)

if response.status_code != 200:
    st.error(f"Грешка при зареждане: {response.status_code} - {response.text}")
else:
    matches = response.json()
    st.markdown(f"Общо заредени мачове: **{len(matches)}**")
    
    value_bets = []

    for match in matches:
        bookmakers = match.get("bookmakers", [])
        pinnacle = next((b for b in bookmakers if b["key"] == "pinnacle"), None)

        if not pinnacle:
            continue

        pinnacle_odds = {o['name']: o['price'] for o in pinnacle['markets'][0]['outcomes']}

        for bookmaker in bookmakers:
            if bookmaker['key'] == "pinnacle":
                continue

            for outcome in bookmaker['markets'][0]['outcomes']:
                name = outcome['name']
                odd = outcome['price']
                pin_odd = pinnacle_odds.get(name)

                if not pin_odd or odd <= pin_odd:
                    continue

                probability = estimate_probability(name, "")
                value = calculate_value(odd, probability)
                diff = odd - pin_odd

                if value > 1.20:
                    value_bets.append({
                        "match": match['home_team'] + " vs " + match['away_team'],
                        "time": match['commence_time'],
                        "selection": name,
                        "bookmaker": bookmaker['key'],
                        "book_odd": odd,
                        "pin_odd": pin_odd,
                        "diff": diff,
                        "prob": probability,
                        "value": value
                    })

    if not value_bets:
        st.warning("Няма намерени стойностни залози.")
    else:
        sorted_bets = sorted(value_bets, key=lambda x: x['value'], reverse=True)

        for bet in sorted_bets:
            match_time = datetime.fromisoformat(bet['time'].replace("Z", "")).strftime("%Y-%m-%d %H:%M")
            st.markdown(f"**{bet['match']} ({match_time})**")
            st.markdown(f"{bet['selection']} при **{bet['bookmaker']}**: {bet['book_odd']} | Pinnacle: {bet['pin_odd']} | "
                        f"Разлика: +{bet['diff']:.2f}")
            st.markdown(f"→ Вероятност: **{bet['prob']}**, Стойност: **{bet['value']:.2f}**")
            st.success("→ Стойностен залог!")
            st.markdown("---")
