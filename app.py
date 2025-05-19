import streamlit as st
import requests
from datetime import datetime
import pytz

ODDS_API_KEY = "ТУК_ПОСТАВИ_СВОЯ_КЛЮЧ"
API_FOOTBALL_KEY = "ТУК_ПОСТАВИ_СВОЯ_КЛЮЧ"

st.title("Стойностни залози с реална статистика")

def get_team_form_percentage(team_name):
    url = "https://v3.football.api-sports.io/teams"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"search": team_name}
    res = requests.get(url, headers=headers, params=params).json()
    if not res["response"]:
        return 0.33
    team_id = res["response"][0]["team"]["id"]
    url_stats = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024"
    res_stats = requests.get(url_stats, headers=headers).json()
    wins = res_stats["response"]["wins"]["total"]
    draws = res_stats["response"]["draws"]["total"]
    losses = res_stats["response"]["loses"]["total"]
    total = wins + draws + losses
    if total == 0:
        return 0.33
    return wins / total

def calculate_probabilities(home_win_pct, away_win_pct):
    prob_home = (home_win_pct + (1 - away_win_pct)) / 2
    prob_away = (away_win_pct + (1 - home_win_pct)) / 2
    prob_draw = 1 - prob_home - prob_away
    if prob_draw < 0:
        prob_draw = 0.1
    return prob_home, prob_draw, prob_away

def get_best_odds_vs_pinnacle(bookmakers, market_key):
    pinnacle_odds = {}
    for bm in bookmakers:
        if bm["key"] == "pinnacle":
            for m in bm["markets"]:
                if m["key"] == market_key:
                    for outcome in m["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]
            break
    if not pinnacle_odds:
        return None
    best_value = -1
    best_bm = None
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
                        if diff > best_value:
                            best_value = diff
                            best_bm = {
                                "bookmaker": bm["title"],
                                "team": name,
                                "price": price,
                                "pinnacle": pinnacle_odds[name],
                                "diff": round(diff, 2)
                            }
    if best_bm and best_bm["diff"] >= 0.1:
        return best_bm
    return None

try:
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "daysFrom": 0,
        "daysTo": 2,
        "apiKey": ODDS_API_KEY,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()

    count_value = 0
    st.header("Всички залози (без филтър):")
    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        commence = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Sofia"))
        bookmakers = match["bookmakers"]

        home_win_pct = get_team_form_percentage(home)
        away_win_pct = get_team_form_percentage(away)
        prob_home, prob_draw, prob_away = calculate_probabilities(home_win_pct, away_win_pct)

        best = get_best_odds_vs_pinnacle(bookmakers, "h2h")
        if best:
            if best["team"] == home:
                prob = prob_home
            elif best["team"] == away:
                prob = prob_away
            else:
                prob = prob_draw
            value = round(prob * best["price"], 2)

            st.markdown(f"### {home} vs {away} ({commence.strftime('%Y-%m-%d %H:%M')})")
            st.markdown(f"""
            **Залог:** {best['team']}  
            **Букмейкър:** {best['bookmaker']}  
            **Коефициент:** {best['price']} (Pinnacle: {best['pinnacle']})  
            **Вероятност:** {prob:.2f}  
            **Стойност:** {value}  
            """)

            if prob >= 0.55 and 1.3 <= best["price"] <= 1.8 and value >= 1.05:
                count_value += 1

    st.header("Стойностни залози (филтрирани):")
    if count_value == 0:
        st.info("Няма намерени стойностни залози със зададените параметри.")
    else:
        st.success(f"Общо намерени стойностни залози: {count_value}")

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
