value_bets_app.py

import streamlit as st
import requests
import datetime
import hashlib
import json
import time from functools
import lru_cache

--- Настройки ---

THE_ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1" FOOTBALL_API_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e" ALLOWED_BOOKMAKERS = ["pinnacle", "betfair", "unibet", "bwin"] MIN_VALUE_THRESHOLD = 0.05 CACHE_EXPIRY = 3600  # секунди

--- Кеш структура ---

cache = {}

def cache_get(key): item = cache.get(key) if item and time.time() - item['timestamp'] < CACHE_EXPIRY: return item['data'] return None

def cache_set(key, data): cache[key] = {'data': data, 'timestamp': time.time()}

--- Изтегляне на мачове от The Odds API ---

def load_odds(): url = f"https://api.the-odds-api.com/v4/sports/soccer/odds" params = { "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal", "dateFormat": "iso", "daysFrom": 0, "daysTo": 3, "apiKey": THE_ODDS_API_KEY } response = requests.get(url, params=params) return response.json() if response.status_code == 200 else []

--- Изтегляне на форма и h2h от API-Football ---

def get_team_form(team_name): cache_key = f"form_{hashlib.md5(team_name.encode()).hexdigest()}" cached = cache_get(cache_key) if cached: return cached

url = f"https://v3.football.api-sports.io/teams?search={team_name}"
headers = {"x-apisports-key": FOOTBALL_API_KEY}
team_data = requests.get(url, headers=headers).json()
try:
    team_id = team_data['response'][0]['team']['id']
except:
    return 0.5  # По подразбиране

url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024"
stat_data = requests.get(url, headers=headers).json()
form = stat_data.get('response', {}).get('form', '')
value = form.count("W") / len(form) if form else 0.5
cache_set(cache_key, value)
return value

--- Оценка на вероятности и стойност ---

def implied_probability(odds): return 1 / odds if odds > 0 else 0

def calculate_value(probability, odds): return (probability * odds) - 1

def estimate_probabilities(form_home, form_away): prob_home = 0.4 + (form_home - form_away) * 0.3 prob_away = 0.4 + (form_away - form_home) * 0.3 prob_draw = 1 - prob_home - prob_away return max(0.05, min(0.8, prob_home)), max(0.05, min(0.8, prob_draw)), max(0.05, min(0.8, prob_away))

--- Филтриране на букмейкъри и пазари ---

def filter_markets_by_bookmaker(bookmakers): return [bm for bm in bookmakers if bm.get('key') in ALLOWED_BOOKMAKERS]

--- Интерфейс на приложението ---

st.title("Детектор на стойностни футболни залози") st.caption("С подобрена оценка на вероятности, кеш и филтриране на букмейкъри")

st.subheader("Зареждане на мачове и коефициенти") data = load_odds()

for match in data: home = match['home_team'] away = match['away_team'] time_str = match['commence_time'] bookmakers = filter_markets_by_bookmaker(match.get('bookmakers', []))

form_home = get_team_form(home)
form_away = get_team_form(away)
prob_home, prob_draw, prob_away = estimate_probabilities(form_home, form_away)

value_bets = []
for bm in bookmakers:
    for market in bm.get('markets', []):
        if market['key'] == 'h2h':
            outcomes = market.get('outcomes', [])
            for out in outcomes:
                if out['name'] == home:
                    val = calculate_value(prob_home, out['price'])
                    if val >= MIN_VALUE_THRESHOLD:
                        value_bets.append((f"Победа за {home}", out['price'], val))
                elif out['name'] == draw_label := 'Draw':
                    val = calculate_value(prob_draw, out['price'])
                    if val >= MIN_VALUE_THRESHOLD:
                        value_bets.append(("Равенство", out['price'], val))
                elif out['name'] == away:
                    val = calculate_value(prob_away, out['price'])
                    if val >= MIN_VALUE_THRESHOLD:
                        value_bets.append((f"Победа за {away}", out['price'], val))

        elif market['key'] == 'totals':
            for out in market.get('outcomes', []):
                if '2.5' in out['name']:
                    prob_over = 0.55  # временно фиксирана вероятност
                    val = calculate_value(prob_over, out['price'])
                    if val >= MIN_VALUE_THRESHOLD:
                        value_bets.append((out['name'], out['price'], val))

if value_bets:
    st.markdown(f"**{home} vs {away}** ({time_str})")
    for desc, odd, val in value_bets:
        st.write(f"- {desc} @ {odd:.2f} (стойност: {val:.2%})")

