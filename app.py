import streamlit as st
import requests
from datetime import datetime, timedelta
import pytz
import time

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

st.title("Стойностни залози с кеширана статистика и оценка")

# --- Кеширане на резултатите за 12 часа ---
@st.cache_data(ttl=43200)  # 12 часа кеш
def get_team_id_cached(team_name, season=2024):
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": team_name, "season": season}
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data["results"] > 0:
            return data["response"][0]["team"]["id"]
    except:
        return None
    return None

@st.cache_data(ttl=43200)  # 12 часа кеш
def get_team_form_cached(team_id, season=2024, last_n=5):
    if not team_id:
        return None
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"team": team_id, "season": season, "last": last_n, "status": "FT"}
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        fixtures = data["response"]
        if not fixtures:
            return None
        wins, draws, losses = 0, 0, 0
        for f in fixtures:
            home_id = f["teams"]["home"]["id"]
            away_id = f["teams"]["away"]["id"]
            home_goals = f["score"]["fulltime"]["home"]
            away_goals = f["score"]["fulltime"]["away"]
            if home_goals is None or away_goals is None:
                continue
            if team_id == home_id:
                if home_goals > away_goals:
                    wins +=1
                elif home_goals == away_goals:
                    draws +=1
                else:
                    losses +=1
            else:
                if away_goals > home_goals:
                    wins +=1
                elif away_goals == home_goals:
                    draws +=1
                else:
                    losses +=1
        total = wins + draws + losses
        if total == 0:
            return None
        form_score = (wins + 0.5 * draws) / total
        return form_score
    except:
        return None

def calc_probabilities(home_form, away_form):
    if home_form is None or away_form is None:
        return 0.33, 0.34, 0.33
    total = home_form + away_form
    if total == 0:
        return 0.33, 0.34, 0.33
    home_prob = home_form / total
    away_prob = away_form / total
    draw_prob = 1 - (home_prob + away_prob)
    if draw_prob < 0:
        draw_prob = 0.1
    return home_prob, draw_prob, away_prob

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

    # Намери най-добър коефициент различен от Pinnacle
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

# --- Зареждане на мачове ---
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
        time_match = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))

        # Вземаме кеширани ID-та и форма
        home_id = get_team_id_cached(home)
        away_id = get_team_id_cached(away)
        home_form = get_team_form_cached(home_id)
        away_form = get_team_form_cached(away_id)

        best = get_best_odds_vs_pinnacle(match["bookmakers"], "h2h")
        if best:
            prob_home, prob_draw, prob_away = calc_probabilities(home_form, away_form)

            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw

            value = round(prob * best["price"], 2)
            color = "green" if value > 1.2 else "white"

            st.markdown(f"### {home} vs {away} ({time_match.strftime('%Y-%m-%d %H:%M')})")
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>"
                f"{best['team']} при {best['bookmaker']} | Коефициент: {best['price']} | Pinnacle: {best['pinnacle']} | Разлика: +{best['diff']}<br>"
                f"Вероятност: {prob:.2f} | Стойност: {value:.2f}"
                f"{' → СТойностен залог!' if value > 1.2 else ''}"
                f"</span>",
                unsafe_allow_html=True
            )
            shown += 1

        # Малка пауза, за да не се претовари API Football
        time.sleep(0.3)

    st.success(f"Общо намерени стойностни залози: {shown}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
