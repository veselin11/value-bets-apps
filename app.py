import streamlit as st
import requests

# Конфигурация
THE_ODDS_API_KEY = "ТВОЯ_API_КЛЮЧ"
BOOKMAKER_PRIORITY = "matchbook"
PINNACLE = "pinnacle"
MIN_PROBABILITY = 0.55  # 55% минимална вероятност

# Функция за зареждане на всички мачове
def load_matches():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": THE_ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"Грешка при заявката: {response.status_code}")
        return []

    return response.json()

# Изчисляване на implied probability
def implied_prob(odds):
    return 1.0 / odds if odds and odds > 0 else 0

# Основна логика
st.title("Стойностни Залози с Над 55% Вероятност")

matches = load_matches()

if not matches:
    st.warning("Няма заредени мачове.")
else:
    for match in matches:
        home = match.get("home_team")
        away = match.get("away_team")

        if not home or not away:
            st.warning(f"Пропуснат мач поради липсващи отбори: {match.get('teams', 'неизвестни')}")
            continue

        bookmakers = match.get("bookmakers", [])
        odds_bookmaker = None
        odds_pinnacle = None

        for book in bookmakers:
            if book["key"] == BOOKMAKER_PRIORITY:
                odds_bookmaker = book["markets"][0]["outcomes"]
            if book["key"] == PINNACLE:
                odds_pinnacle = book["markets"][0]["outcomes"]

        if not odds_bookmaker or not odds_pinnacle:
            continue

        # Създай речници по име
        bm_odds = {o["name"]: o["price"] for o in odds_bookmaker}
        pin_odds = {o["name"]: o["price"] for o in odds_pinnacle}

        for outcome in ["Draw", home, away]:
            user_odd = bm_odds.get(outcome)
            pin_odd = pin_odds.get(outcome)

            if not user_odd or not pin_odd:
                continue

            probability = implied_prob(pin_odd)
            if probability < MIN_PROBABILITY:
                continue

            value = user_odd * probability

            if value > 1.05:
                st.markdown(f"### {home} vs {away}")
                st.markdown(
                    f"**{outcome}** при {BOOKMAKER_PRIORITY}: {user_odd} | {PINNACLE}: {pin_odd} | "
                    f"Разлика: +{round(user_odd - pin_odd, 2)}"
                )
                st.markdown(
                    f"→ Вероятност: {round(probability, 2)}, Стойност: {round(value, 2)} → **Стойностен залог!**"
                )
                st.divider()
