import streamlit as st
import requests
from datetime import datetime
import pytz

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

st.title("Стойностни залози чрез сравнение с Pinnacle + Форма & H2H")

# API-Football headers
FOOTBALL_API_HEADERS = {
    "X-RapidAPI-Key": API_FOOTBALL_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Сесийно състояние за бутон презареждане
if "reload" not in st.session_state:
    st.session_state.reload = False

if st.button("Презареди прогнози"):
    st.session_state.reload = True

if st.session_state.reload:
    st.session_state.reload = False
    st.experimental_rerun()

# Намиране на ID на отбор
def get_team_id(team_name):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    params = {"search": team_name}
    res = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)
    teams = res.json().get("response", [])
    for team in teams:
        if team["team"]["name"].lower() == team_name.lower():
            return team["team"]["id"]
    return None

# Последни 5 мача на отбор
def get_last_matches(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"team": team_id, "season": 2024, "last": 5}
    res = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)
    return res.json().get("response", [])

# Последни директни срещи
def get_h2h(home_id, away_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead"
    params = {"h2h": f"{home_id}-{away_id}", "last": 3}
    res = requests.get(url, headers=FOOTBALL_API_HEADERS, params=params)
    return res.json().get("response", [])

# Вероятности от статистика
def calculate_probabilities_from_stats(home_team, away_team):
    try:
        home_id = get_team_id(home_team)
        away_id = get_team_id(away_team)
        if not home_id or not away_id:
            return 0.33, 0.34, 0.33

        home_matches = get_last_matches(home_id)
        away_matches = get_last_matches(away_id)
        h2h_matches = get_h2h(home_id, away_id)

        def points(matches, team_id):
            score = 0
            for m in matches:
                res = m["teams"]
                goals = m["goals"]
                if res["home"]["id"] == team_id:
                    if goals["home"] > goals["away"]: score += 3
                    elif goals["home"] == goals["away"]: score += 1
                else:
                    if goals["away"] > goals["home"]: score += 3
                    elif goals["away"] == goals["home"]: score += 1
            return score

        home_pts = points(home_matches, home_id)
        away_pts = points(away_matches, away_id)

        h2h_score = 0
        for m in h2h_matches:
            res = m["teams"]
            goals = m["goals"]
            if goals["home"] == goals["away"]:
                h2h_score += 0.5
            elif (res["home"]["id"] == home_id and goals["home"] > goals["away"]) or \
                 (res["away"]["id"] == home_id and goals["away"] > goals["home"]):
                h2h_score += 1
            else:
                h2h_score -= 1

        total = home_pts + away_pts + abs(h2h_score) + 0.01
        prob_home = (home_pts + h2h_score) / total
        prob_away = away_pts / total
        prob_draw = 1 - prob_home - prob_away
        return round(prob_home, 2), round(prob_draw, 2), round(prob_away, 2)

    except Exception as e:
        st.warning(f"Грешка в статистиката за {home_team} vs {away_team}: {e}")
        return 0.33, 0.34, 0.33

# Сравнение с Pinnacle
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

# Извличане на мачове
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
        time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")
        if best:
            prob_home, prob_draw, prob_away = calculate_probabilities_from_stats(home, away)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)
            color = "green" if value > 1.2 else "black"

            st.markdown(f"### {home} vs {away} ({time.strftime('%Y-%m-%d %H:%M')})")
            st.markdown(
                f"<span style='color:{color}'>"
                f"{best['team']} при {best['bookmaker']}: {best['price']} | Pinnacle: {best['pinnacle']} | "
                f"Разлика: +{best['diff']}<br>"
                f"→ Вероятност: {prob:.2f}, Стойност: {value:.2f}"
                f"{' → <strong>Стойностен залог!</strong>' if value > 1.2 else ''}"
                f"</span>",
                unsafe_allow_html=True
            )
            shown += 1

    st.success(f"Общо стойностни предложения: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
