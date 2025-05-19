import streamlit as st
import requests
from datetime import datetime
import pytz

# Постави тук своя реален ключ от The Odds API
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

st.title("Стойностни залози с реална статистика и оценка")

def get_probabilities(home_form, away_form):
    # Примерна по-умна оценка на вероятности (може да се подобри)
    total = home_form + away_form
    prob_home = home_form / total
    prob_away = away_form / total
    prob_draw = 1 - prob_home - prob_away
    return prob_home, prob_draw, prob_away

def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    best_diff = -1
    best_bookmaker = None

    # Намери Pinnacle
    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            for m in bm["markets"]:
                if m["key"] == market_key:
                    for outcome in m["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]
            break

    if not pinnacle_odds:
        return None

    # Намери най-добра оферта от другите
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
                            best_bookmaker = {
                                "bookmaker": bm["key"],
                                "team": name,
                                "price": price,
                                "pinnacle": pinnacle_odds[name],
                                "diff": round(diff, 2)
                            }
    return best_bookmaker if best_bookmaker and best_bookmaker["diff"] >= 0 else None

url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 2,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()
    shown = 0

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))

        # За пример: оценка на форма (тук просто примерни числа, замени с реални данни)
        home_form = 0.6
        away_form = 0.4

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")

        # Показваме ВСИЧКИ залози, без филтър, за да видим реалните стойности
        if best:
            prob_home, prob_draw, prob_away = get_probabilities(home_form, away_form)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)
            color = "green" if value > 1.05 else "black"

            st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
            st.markdown(
                f"<span style='color:{color}'>"
                f"{best['team']} при {best['bookmaker']}: {best['price']} | Pinnacle: {best['pinnacle']} | "
                f"Разлика: +{best['diff']}<br>"
                f"→ Вероятност: {prob:.2f}, Стойност: {value:.2f}"
                f"{' → <strong>Стойностен залог!</strong>' if value > 1.05 else ''}"
                f"</span>",
                unsafe_allow_html=True
            )
            shown += 1

    st.success(f"Общо залози показани: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
