import streamlit as st
import requests
import json
import os
from datetime import datetime
from time import sleep

# --- Ключове от secrets ---
ODDS_API_KEY = st.secrets["odds_api_key"]
API_FOOTBALL_KEY = st.secrets["api_football_key"]

ALLOWED_BOOKMAKERS = ["betfair", "pinnacle", "bet365", "williamhill"]
CACHE_FILE = "stats_cache.json"

# --- Зареждане кеш ---
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        stats_cache = json.load(f)
else:
    stats_cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(stats_cache, f)

# --- Функция за кеширане и взимане на данни от API-Football ---
def get_api_football(endpoint, params=None):
    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_FOOTBALL_KEY
    }
    url = f"{base_url}/{endpoint}"
    key = f"{url}_{json.dumps(params, sort_keys=True)}"
    if key in stats_cache:
        return stats_cache[key]

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        stats_cache[key] = data
        save_cache()
        sleep(1)  # Пауза за rate limit
        return data
    else:
        st.warning(f"Грешка при API-Football: {response.status_code} {response.text}")
        return None

# --- Вземане на последни 5 мача (форма) на отбор ---
def get_team_form(team_name):
    data = get_api_football("teams", {"search": team_name})
    if not data or not data["response"]:
        return []
    team_id = data["response"][0]["team"]["id"]
    matches_data = get_api_football("fixtures", {"team": team_id, "last": 5})
    if not matches_data or not matches_data["response"]:
        return []
    return matches_data["response"]

# --- Вземане на head to head между два отбора ---
def get_h2h(home_team, away_team):
    home_data = get_api_football("teams", {"search": home_team})
    away_data = get_api_football("teams", {"search": away_team})
    if not home_data or not away_data or not home_data["response"] or not away_data["response"]:
        return None
    home_id = home_data["response"][0]["team"]["id"]
    away_id = away_data["response"][0]["team"]["id"]
    h2h_data = get_api_football("fixtures/headtohead", {"h2h": f"{home_id}-{away_id}"})
    if not h2h_data or not h2h_data["response"]:
        return None
    return h2h_data["response"]

# --- Изчисляване на вероятности по прост модел (на база форма и H2H) ---
def calc_probabilities(home_form, away_form, h2h):
    def form_stats(matches, team_name):
        wins = draws = losses = 0
        for m in matches:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            goals_home = m["goals"]["home"]
            goals_away = m["goals"]["away"]
            if goals_home is None or goals_away is None:
                continue
            if team_name == home:
                if goals_home > goals_away:
                    wins += 1
                elif goals_home == goals_away:
                    draws += 1
                else:
                    losses += 1
            elif team_name == away:
                if goals_away > goals_home:
                    wins += 1
                elif goals_away == goals_home:
                    draws += 1
                else:
                    losses += 1
        total = wins + draws + losses
        return wins, draws, losses, total

    home_team_name = home_form[0]["teams"]["home"]["name"] if home_form else ""
    away_team_name = away_form[0]["teams"]["home"]["name"] if away_form else ""

    home_w, home_d, home_l, home_t = form_stats(home_form, home_team_name)
    away_w, away_d, away_l, away_t = form_stats(away_form, away_team_name)

    h2h_w = h2h_d = h2h_l = 0
    for match in h2h or []:
        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]
        if home_goals is None or away_goals is None:
            continue
        if home_goals > away_goals:
            h2h_w += 1
        elif home_goals == away_goals:
            h2h_d += 1
        else:
            h2h_l += 1
    h2h_t = h2h_w + h2h_d + h2h_l

    total_home = (home_w + 0.5 * home_d) / max(home_t,1)
    total_away = (away_w + 0.5 * away_d) / max(away_t,1)
    total_h2h = (h2h_w + 0.5 * h2h_d) / max(h2h_t,1)

    prob_home_win = round(0.5 * total_home + 0.5 * total_h2h, 2)
    prob_away_win = round(0.5 * total_away + 0.5 * (1 - total_h2h), 2)
    prob_draw = round(1 - prob_home_win - prob_away_win, 2)
    if prob_draw < 0:
        prob_draw = 0.0

    return prob_home_win, prob_draw, prob_away_win

# --- Изчисление на Kelly формула за залог ---
def kelly_criterion(prob, odds, bankroll=1000):
    b = odds - 1
    kelly = (b * prob - (1 - prob)) / b
    return max(kelly, 0) * bankroll

# --- Филтриране пазари и букмейкъри ---
def filter_markets_by_bookmaker(bookmakers):
    filtered_markets = []
    for bookmaker in bookmakers:
        if bookmaker.get('key') in ALLOWED_BOOKMAKERS:
            for market in bookmaker.get('markets', []):
                # Премахваме "goal/goal" пазари
                if market['key'] in ['h2h', 'totals']:
                    filtered_markets.append({
                        'bookmaker': bookmaker['title'],
                        'key': market['key'],
                        'outcomes': market['outcomes']
                    })
    return filtered_markets

# --- Основно приложение --- #
st.title("Детектор на стойностни футболни залози с реална статистика")

st.markdown("### Зареждане на футболни мачове и коефициенти от The Odds API")

odds_url = f"https://api.the-odds-api.com/v4/sports/soccer/odds"
params = {
    "regions": "eu",
    "markets": "h2h,totals",
    "oddsFormat": "decimal",
    "dateFormat": "iso",
    "daysFrom": 0,
    "daysTo": 3,
    "apiKey": ODDS_API_KEY
}

try:
    response = requests.get(odds_url, params=params)
    response.raise_for_status()
    matches = response.json()

    if not matches:
        st.warning("Няма намерени мачове или няма налични пазари.")
    else:
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            commence = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
            time_str = commence.strftime('%Y-%m-%d %H:%M')

            st.markdown(f"## {home} vs {away} ({time_str})")

            bookmakers = match.get('bookmakers', [])
            markets = filter_markets_by_bookmaker(bookmakers)

            if not markets:
                st.write("❌ Пропуснат мач – няма пазари от избраните букмейкъри.")
                continue

            home_form = get_team_form(home)
            away_form = get_team_form(away)
            h2h = get_h2h(home, away)

            prob_home, prob_draw,
