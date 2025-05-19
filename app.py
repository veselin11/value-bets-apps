import streamlit as st
import requests
from datetime import datetime
import pytz

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

st.title("Стойностни залози чрез сравнение с Pinnacle и по-умна оценка")

# --- Функция за реална оценка на вероятностите (примерно с форма, може да се надгражда) ---
def get_probabilities(home_stats, away_stats):
    # Примерна логика: ако домакинът има по-добра форма, по-голяма вероятност за победа
    if home_stats["form_rank"] < away_stats["form_rank"]:
        return 0.55, 0.25, 0.20  # домакин силен
    elif away_stats["form_rank"] < home_stats["form_rank"]:
        return 0.20, 0.25, 0.55  # гост силен
    else:
        return 0.33, 0.34, 0.33   # равенство или близки

# --- Извличане на коефициенти и сравнение с Pinnacle ---
def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    best_diff = -1
    best_bookmaker = None

    # Намери Pinnacle коефициенти
    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            for m in bm["markets"]:
                if m["key"] == market_key:
                    for outcome in m["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]
            break

    if not pinnacle_odds:
        return None

    # Търси най-добра оферта, която е значително по-висока от Pinnacle
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
    # Филтър за минимална разлика, за да е залогът стойностен
    return best_bookmaker if best_bookmaker and best_bookmaker["diff"] >= 0.2 else None

# --- Примерна функция за извличане на статистика (тук е просто фиктивна, трябва да се добави реална интеграция) ---
def get_team_stats(team_name):
    # Примерни данни, може да замениш с реално извличане от API-Football
    dummy_stats = {
        "form_rank": hash(team_name) % 10  # просто рандом стойност за пример
    }
    return dummy_stats

# --- Основен код ---
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

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")
        if best:
            home_stats = get_team_stats(home)
            away_stats = get_team_stats(away)
            prob_home, prob_draw, prob_away = get_probabilities(home_stats, away_stats)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)

            # Филтриране за по-висока вероятност и адекватни коефициенти
            if prob >= 0.55 and 1.3 <= best["price"] <= 1.8 and value >= 1.05:
                color = "green"
                st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
                st.markdown(
                    f"<span style='color:{color}'>"
                    f"{best['team']} при {best['bookmaker']}: {best['price']} | Pinnacle: {best['pinnacle']} | "
                    f"Разлика: +{best['diff']}<br>"
                    f"→ Вероятност: {prob:.2f}, Стойност: {value:.2f}"
                    f" → <strong>Стойностен залог!</strong>"
                    f"</span>",
                    unsafe_allow_html=True
                )
                shown += 1

    if shown == 0:
        st.info("Няма намерени стойностни залози със зададените параметри.")
    else:
        st.success(f"Общо стойностни предложения: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
