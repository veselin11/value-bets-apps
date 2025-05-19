import streamlit as st
import requests
from datetime import datetime

st.title("Детектор на стойностни футболни залози")

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

def get_matches(sport_key, markets):
    odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "eu",
        "markets": markets,
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "daysFrom": 0,
        "daysTo": 3,
        "apiKey": ODDS_API_KEY
    }
    try:
        response = requests.get(odds_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 422 and ',' in markets:
            if markets != "h2h":
                st.warning(f"Пазарите '{markets}' не са налични, опитвам само с 'h2h'.")
                return get_matches(sport_key, "h2h")
        st.warning(f"Пропуснат спорт с ключ {sport_key} за пазар {markets} (грешка {response.status_code})")
        return []

def simple_probability_estimate():
    # Това е мястото да сложим реална формула или ML модел.
    # За пример ще върнем фиксирана вероятност за домакинска победа 0.5 (50%)
    # и равенство 0.25, гост 0.25.
    return {"home_win": 0.5, "draw": 0.25, "away_win": 0.25}

def is_value_bet(bookmaker_odds, prob):
    # Проверяваме дали коефициентът е по-голям от 1 / вероятност
    threshold = 1 / prob if prob > 0 else float('inf')
    return bookmaker_odds > threshold

try:
    sports_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    response = requests.get(sports_url)
    response.raise_for_status()
    sports = response.json()

    football_sports = [sport for sport in sports if "soccer" in sport['key'].lower()]
    if not football_sports:
        st.write("Не са намерени футболни спортове.")
    else:
        for sport in football_sports:
            sport_key = sport['key']
            sport_title = sport['title']
            st.header(f"Лига: {sport_title}")

            matches = get_matches(sport_key, "h2h,totals")
            if not matches:
                st.write("  Няма мачове или грешка при зареждане.")
                continue

            st.write(f"Намерени мачове: {len(matches)}")

            for match in matches:
                home = match['home_team']
                away = match['away_team']
                start_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')

                st.subheader(f"{home} vs {away} - {start_time}")

                # Примерна оценка на вероятности
                probs = simple_probability_estimate()

                # Търсим коефициенти от първия букмейкър (пример)
                if 'bookmakers' in match and len(match['bookmakers']) > 0:
                    bookmaker = match['bookmakers'][0]
                    markets = bookmaker.get('markets', [])

                    for market in markets:
                        if market['key'] == 'h2h':
                            outcomes = market['outcomes']
                            for outcome in outcomes:
                                name = outcome['name'].lower()
                                odd = outcome['price']
                                prob = 0
                                if 'home' in name:
                                    prob = probs['home_win']
                                elif 'draw' in name:
                                    prob = probs['draw']
                                elif 'away' in name:
                                    prob = probs['away_win']

                                if is_value_bet(odd, prob):
                                    st.markdown(f"**Value Bet:** {name.capitalize()} с коефициент {odd} (очаквана вероятност {prob*100:.1f}%)")
                                else:
                                    st.write(f"{name.capitalize()} - коефициент: {odd}")

except Exception as e:
    st.error(f"Грешка: {e}")
