import streamlit as st
import requests
from datetime import datetime
import pytz

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

st.title("Стойностни залози чрез сравнение с Pinnacle")

# --- Оценка на вероятностите (примерна, базирана на форма)
def get_probabilities(home_form, away_form):
    # По-прецизна логика може да се добави
    if home_form < away_form:
        return 0.45, 0.3, 0.25
    elif away_form < home_form:
        return 0.25, 0.3, 0.45
    else:
        return 0.33, 0.34, 0.33

# --- Намиране на най-добри коефициенти спрямо Pinnacle ---
def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    best_diff = -1
    best_bet = None

    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            for m in bm["markets"]:
                if m["key"] == market_key:
                    for outcome in m["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]
            break

    if not pinnacle_odds:
        return None

    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            continue
        for m in bm["markets"]:
            if m["key"] == market_key:
                for outcome in m["outcomes"]:
                    name = outcome["name"]
                    price = outcome["price"]
                    if name in pinnacle_odds:
                        diff = price - pinnacle_odds[name]
                        if diff > best_diff:
                            best_diff = diff
                            best_bet = {
                                "bookmaker": bm["key"],
                                "team": name,
                                "price": price,
                                "pinnacle": pinnacle_odds[name],
                                "diff": round(diff, 2)
                            }
    # Филтър по минимална разлика
    if best_bet and best_bet["diff"] >= 0.2:
        return best_bet
    return None

# --- Заявка към The Odds API с корекция за хедър ---
url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
headers = {
    "x-api-key": ODDS_API_KEY
}
params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 2
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    matches = response.json()

    shown = 0
    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        # Примерни стойности за форма (трябва да се заменят с реална статистика)
        home_form = len(home)  # Просто за демонстрация
        away_form = len(away)

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")
        if best:
            prob_home, prob_draw, prob_away = get_probabilities(home_form, away_form)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)

            # Приложение на прагова стратегия
            if prob >= 0.55 and 1.3 <= best["price"] <= 1.8 and value >= 1.05:
                color = "green"
                label = " → Стойностен залог!"
            else:
                color = "white"
                label = ""

            time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))

            st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
            st.markdown(
                f"<span style='color:{color}'>"
                f"{best['team']} при {best['bookmaker']}: {best['price']} | Pinnacle: {best['pinnacle']} | "
                f"Разлика: +{best['diff']}<br>"
                f"→ Вероятност: {prob:.2f}, Стойност: {value:.2f}"
                f"{label}"
                f"</span>",
                unsafe_allow_html=True
            )
            shown += 1

    st.success(f"Общо стойностни предложения: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
