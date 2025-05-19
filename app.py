import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# API ключове
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
FOOTBALL_DATA_API_KEY = "e004e3601abd4b108a653f9f3a8c5ede"

# Лиги
LEAGUE_MAPPING = {
    "English Premier League": "soccer_epl",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
    "Ligue 1": "soccer_france_ligue_one",
    "Primeira Liga": "soccer_portugal_primeira_liga",
    "Eredivisie": "soccer_netherlands_eredivisie"
}

# Кеширане
@st.cache_data(ttl=3600)
def get_odds(league_key):
    url = f"https://api.the-odds-api.com/v4/sports/{league_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,over_under_2.5",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data(ttl=3600)
def get_team_flashscore_url(team_name):
    search_url = f"https://www.flashscore.com/search/?q={team_name.replace(' ', '%20')}"
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        if "/team/" in link["href"] and "/results/" not in link["href"]:
            return "https://www.flashscore.com" + link["href"] + "results/"
    return None

@st.cache_data(ttl=3600)
def get_team_form(team_name):
    url = get_team_flashscore_url(team_name)
    if not url:
        return None
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return None
    results = re.findall(r'class="event__part event__part--home event__part--(win|draw|loss)"', response.text)
    points = sum([3 if r == "win" else 1 if r == "draw" else 0 for r in results[:5]])
    return round(points / 15, 2) if results else None

@st.cache_data(ttl=3600)
def get_head_to_head(home_team, away_team):
    return {
        "matches": 5,
        "home_wins": 2,
        "draws": 2,
        "away_wins": 1
    }

def calculate_probability(form_home, form_away, h2h):
    score_home = form_home * 0.6 + (h2h["home_wins"] / h2h["matches"]) * 0.4
    score_away = form_away * 0.6 + (h2h["away_wins"] / h2h["matches"]) * 0.4
    total = score_home + score_away
    return (score_home / total, score_away / total) if total > 0 else (0.5, 0.5)

def is_value_bet(prob, odd, threshold=0.05):
    value = (prob * odd) - 1
    return value > threshold, round(value, 2)

def main():
    st.title("Детектор на стойностни футболни залози")
    st.write("Зареждане на мачове и коефициенти...")

    for league_name, league_key in LEAGUE_MAPPING.items():
        with st.spinner(f"Обработка на {league_name}..."):
            st.subheader(f"Лига: {league_name}")
            matches = get_odds(league_key)
            if not matches:
                st.write("Няма мачове или грешка при зареждане.")
                continue

            value_bets_found = 0

            for match in matches:
                home_team = match.get("home_team")
                away_team = match.get("away_team")
                start_time = match.get("commence_time")
                match_time = datetime.fromisoformat(start_time[:-1]) if start_time else "?"

                st.markdown(f"### {home_team} vs {away_team}")
                st.write(f"Начален час: {match_time}")
                
                if not match.get("bookmakers"):
                    continue

                markets = {}
                for bookmaker in match["bookmakers"]:
                    for market in bookmaker["markets"]:
                        markets[market["key"]] = market

                form_home = get_team_form(home_team) or 0.5
                form_away = get_team_form(away_team) or 0.5
                h2h = get_head_to_head(home_team, away_team)
                prob_home, prob_away = calculate_probability(form_home, form_away, h2h)

                st.write(f"Форма {home_team}: {form_home}")
                st.write(f"Форма {away_team}: {form_away}")
                st.write(f"H2H: {h2h['home_wins']} домакин | {h2h['draws']} равенства | {h2h['away_wins']} гост")

                # H2H пазари
                if "h2h" in markets:
                    for outcome in markets["h2h"]["outcomes"]:
                        team = outcome["name"]
                        odd = outcome["price"]
                        prob = prob_home if team == home_team else prob_away
                        is_value, value = is_value_bet(prob, odd)
                        if is_value:
                            st.success(f"Стойностен залог: {team} @ {odd} | Стойност: {value}")
                            value_bets_found += 1

                # Over/Under 2.5 пазари
                if "over_under_2.5" in markets:
                    for outcome in markets["over_under_2.5"]["outcomes"]:
                        name = outcome["name"]
                        odd = outcome["price"]
                        prob = 0.52 if name == "Over 2.5" else 0.48  # фиктивна вероятност, може да се подобри
                        is_value, value = is_value_bet(prob, odd)
                        if is_value:
                            st.success(f"Стойностен залог: {name} @ {odd} | Стойност: {value}")
                            value_bets_found += 1

            st.write(f"Общо стойностни залози в лигата: {value_bets_found}")

if __name__ == "__main__":
    main()
