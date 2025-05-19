import requests import json import os from datetime import datetime, timedelta

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

Ограничени букмейкъри

ALLOWED_BOOKMAKERS = ["bet365", "pinnacle", "unibet"]

Кеширане

CACHE_FILE = "stats_cache.json"

def load_cache(filename): if os.path.exists(filename): with open(filename, 'r') as f: return json.load(f) return {}

def save_cache(filename, data): with open(filename, 'w') as f: json.dump(data, f)

def get_cached_or_fetch(key, fetch_function): cache = load_cache(CACHE_FILE) now = datetime.utcnow()

if key in cache:
    cached_time = datetime.fromisoformat(cache[key]['timestamp'])
    if now - cached_time < timedelta(hours=6):
        return cache[key]['data']

data = fetch_function()
cache[key] = {'timestamp': now.isoformat(), 'data': data}
save_cache(CACHE_FILE, cache)
return data

def estimate_probability(home_stats, away_stats, league_avg=None): if home_stats and away_stats: home_win_rate = home_stats['wins'] / home_stats['games'] if home_stats['games'] > 0 else 0 away_loss_rate = away_stats['losses'] / away_stats['games'] if away_stats['games'] > 0 else 0 return round((home_win_rate + away_loss_rate) / 2, 3) elif league_avg: return round(league_avg['home_win_rate'], 3) return 0.50

def filter_markets_by_bookmaker(markets): return [m for m in markets if m['bookmaker_key'] in ALLOWED_BOOKMAKERS]

Зареждане на футболните лиги

sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}" sports_response = requests.get(sports_url) sports = [s for s in sports_response.json() if s['group'] == 'Soccer']

print("Стойностни футболни залози с кеш и филтриран букмейкър:")

for sport in sports: sport_key = sport['key'] print(f"\nЛига: {sport['title']}")

odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
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
    odds_response = requests.get(odds_url, params=params)
    odds_response.raise_for_status()
    matches = odds_response.json()

    if not matches:
        print("  Няма активни мачове или пазарите не са налични.")
        continue

    for match in matches:
        home = match['home_team']
        away = match['away_team']
        start_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')

        markets = filter_markets_by_bookmaker(match.get('bookmakers', []))
        for market in markets:
            for outcome in market['markets'][0]['outcomes']:
                team = outcome['name']
                odds = outcome['price']
                implied_prob = round(1 / odds, 3)

                # Примерни фалшиви статистики (замени с реални при fetch)
                home_stats = {'wins': 3, 'games': 5, 'losses': 2}
                away_stats = {'wins': 1, 'games': 5, 'losses': 4}
                probability = estimate_probability(home_stats, away_stats)

                value = round(probability - implied_prob, 3)
                if value > 0.05:
                    print(f"  {home} vs {away} ({start_time})")
                    print(f"    {team} @ {odds} (стойност: {value}) при {market['bookmaker_key']}")

except requests.RequestException as e:
    print(f"  Грешка при зареждане на мачовете: {e}")

