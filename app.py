import streamlit as st
import requests
from datetime import datetime
import pytz

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

st.title("Стойностни залози чрез сравнение с Pinnacle и вероятност")

# --- Примерна оценка на вероятност по форма и голове ---
def estimate_probability(home_stats, away_stats):
    form_score = (home_stats["form"] * 0.6) + (1 - away_stats["form"]) * 0.4
    goal_diff = home_stats["avg_goals_scored"] - away_stats["avg_goals_conceded"]
    probability = min(0.95, max(0.4, 0.5 + form_score * 0.3 + goal_diff * 0.2))
    return round(probability, 2)

# --- Демонстрационни статистики (в реален код ще се ползва API-Football) ---
def get_team_stats(team):
    demo_stats = {
        "form": 0.7,
        "avg_goals_scored": 1.6,
        "avg_goals_conceded": 1.1
    }
    return demo_stats

# --- Нашата оценка за пазар ---
def get_probabilities(home, away, team):
    home_stats = get_team_stats(home)
    away_stats = get_team_stats(away)

    if team == home:
        return estimate_probability(home_stats, away_stats)
    elif team == away:
        return estimate_probability(away_stats, home_stats)
    else:
        return 0.25

# --- Извличане на най-добри коефициенти срещу Pinnacle ---
def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    best_diff = -1
    best_bookmaker = None

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
                            best_bookmaker = {
                                "bookmaker": bm["key"],
                                "team": name,
                                "price": price,
                                "pinnacle": pinnacle_odds[name],
                                "diff": round(diff, 2)
                            }
    return best_bookmaker if best_bookmaker and best_bookmaker["diff"] >= 0.2 else None

# --- Извличане на мачове от The Odds API ---
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h,totals",
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

        for market_key in ["h2h", "totals"]:
            best = get_best_odds_vs_pinnacle(match["bookmakers"], market_key)
            if best:
                prob = get_probabilities(home, away, best["team"])
                value = round(prob * best["price"], 2)
                color = "green" if value > 1.2 and prob >= 0.7 else "white"

                if value > 1.2 and prob >= 0.7:
                    st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
                    st.markdown(
                        f"<span style='color:{color}'>"
                        f"{best['team']} при {best['bookmaker']}: {best['price']} | Pinnacle: {best['pinnacle']} | "
                        f"Разлика: +{best['diff']}<br>"
                        f"→ Вероятност: {prob:.2f}, Стойност: {value:.2f} → <strong>Стойностен залог!</strong>"
                        f"</span>",
                        unsafe_allow_html=True
                    )
                    shown += 1

    st.success(f"Общо стойностни предложения: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
    
