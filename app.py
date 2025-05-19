import streamlit as st
import requests
from datetime import datetime
import pytz

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7d025e6e"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

st.title("Стойностни залози чрез сравнение с Pinnacle")

# --- Функция за реална оценка на вероятностите, базирана на форма (пример) ---
def get_probabilities(home_form, away_form):
    # Пример: по-добрата форма дава по-голяма вероятност за успех
    home_strength = sum(home_form)/len(home_form) if home_form else 0.5
    away_strength = sum(away_form)/len(away_form) if away_form else 0.5

    if home_strength > away_strength:
        return 0.55, 0.25, 0.20
    elif away_strength > home_strength:
        return 0.20, 0.25, 0.55
    else:
        return 0.33, 0.34, 0.33

# --- Фиктивна функция за вземане на форма на отбори (пример, може да се замени с API) ---
def get_team_form(team_name):
    # Тук можеш да добавиш реална логика или API повикване за последни резултати
    # За момента връщаме фиктивни стойности от 0 до 1 (успехи в последните 5 мача)
    dummy_data = {
        "Team A": [1, 1, 0.5, 1, 0.5],
        "Team B": [0.5, 0, 0, 0.5, 0],
        "Team C": [0, 1, 0, 1, 0.5],
        "Team D": [1, 1, 1, 1, 1],
        # Можеш да разшириш по реални отбори
    }
    return dummy_data.get(team_name, [0.5, 0.5, 0.5, 0.5, 0.5])

# --- Извличане на най-добри коефициенти спрямо Pinnacle ---
def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    best_diff = -1
    best_bookmaker = None

    # 1. Вземи Pinnacle коефициенти
    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            for m in bm["markets"]:
                if m["key"] == market_key:
                    for outcome in m["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]
            break

    if not pinnacle_odds:
        return None

    # 2. Намери най-добрата оферта с по-голяма цена от Pinnacle
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
    # Филтър за минимална разлика
    return best_bookmaker if best_bookmaker and best_bookmaker["diff"] >= 0.1 else None

# --- Извличане на мачове ---
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
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
        time_match = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")
        if best:
            home_form = get_team_form(home)
            away_form = get_team_form(away)

            prob_home, prob_draw, prob_away = get_probabilities(home_form, away_form)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)

            # Филтриране по прагова стратегия:
            if prob >= 0.55 and 1.3 <= best["price"] <= 1.8 and value >= 1.05:
                color = "green"
                st.markdown(f"### {home} vs {away} ({time_match.strftime('%Y-%m-%d %H:%M')})")
                st.markdown(
                    f"<span style='color:{color}; font-weight:bold;'>"
                    f"{best['team']} при {best['bookmaker']} | Коефициент: {best['price']} | Pinnacle: {best['pinnacle']} | Разлика: +{best['diff']}<br>"
                    f"Вероятност: {prob:.2f} | Стойност: {value:.2f} → СТойностен залог!"
                    f"</span>",
                    unsafe_allow_html=True
                )
                shown += 1

    if shown == 0:
        st.warning("Не са намерени стойностни залози с избраните критерии.")
    else:
        st.success(f"Общо стойностни предложения: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
