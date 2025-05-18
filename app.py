import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {'User-Agent': 'Mozilla/5.0'}

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"  # Твой API ключ
API_URL = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/"  # Ще минаваме през различни лиги

EURO_LEAGUES = {
    'soccer_epl': 'English Premier League',
    'soccer_spain_la_liga': 'La Liga',
    'soccer_italy_serie_a': 'Serie A',
    'soccer_germany_bundesliga': 'Bundesliga',
    'soccer_france_ligue_one': 'Ligue 1',
    'soccer_portugal_primeira_liga': 'Primeira Liga',
    'soccer_netherlands_eredivisie': 'Eredivisie'
}

# --- Функции за flashscore ---

def get_team_form(team_name, max_matches=5):
    try:
        search_url = f"https://www.flashscore.com/search/?q={team_name.replace(' ', '%20')}"
        resp = requests.get(search_url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        team_link = None
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/team/' in href:
                team_link = "https://www.flashscore.com" + href
                break
        if not team_link:
            return []
        team_resp = requests.get(team_link, headers=HEADERS, timeout=5)
        team_soup = BeautifulSoup(team_resp.text, 'html.parser')
        matches = []
        for match_div in team_soup.select('.event__match')[:max_matches]:
            date = match_div.select_one('.event__time').text.strip() if match_div.select_one('.event__time') else ''
            home = match_div.select_one('.event__participant--home').text.strip() if match_div.select_one('.event__participant--home') else ''
            away = match_div.select_one('.event__participant--away').text.strip() if match_div.select_one('.event__participant--away') else ''
            score_el = match_div.select_one('.event__scores')
            score = score_el.text.strip() if score_el else 'N/A'
            matches.append({'date': date, 'home': home, 'away': away, 'score': score})
        return matches
    except Exception:
        return []

def get_head_to_head(team1, team2, max_matches=5):
    try:
        t1 = team1.lower().replace(' ', '-')
        t2 = team2.lower().replace(' ', '-')
        h2h_url = f"https://www.flashscore.com/match-up/{t1}-{t2}/"
        resp = requests.get(h2h_url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = []
        for match_div in soup.select('.event__match--oneLine')[:max_matches]:
            date = match_div.select_one('.event__time').text.strip() if match_div.select_one('.event__time') else ''
            home = match_div.select_one('.event__participant--home').text.strip() if match_div.select_one('.event__participant--home') else ''
            away = match_div.select_one('.event__participant--away').text.strip() if match_div.select_one('.event__participant--away') else ''
            score_el = match_div.select_one('.event__scores')
            score = score_el.text.strip() if score_el else 'N/A'
            matches.append({'date': date, 'home': home, 'away': away, 'score': score})
        return matches
    except Exception:
        return []

def calculate_form_strength(matches, team_name):
    wins = 0
    total = 0
    for match in matches:
        score = match['score']
        if score == 'N/A':
            continue
        try:
            home_goals, away_goals = map(int, score.split(':'))
        except:
            continue
        total += 1
        if match['home'] == team_name and home_goals > away_goals:
            wins += 1
        elif match['away'] == team_name and away_goals > home_goals:
            wins += 1
    return wins / total if total > 0 else 0

def combined_probability(form_strength, h2h_strength, odds):
    estimated_prob = 0.6 * form_strength + 0.4 * h2h_strength
    implied_prob = 1 / odds if odds > 0 else 0
    value = estimated_prob - implied_prob
    return estimated_prob, value

# --- Функция за зареждане на мачове от The Odds API за една лига ---

def get_matches_from_odds_api(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "totals,h2h",
        "oddsFormat": "decimal"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Грешка при зареждане от The Odds API: {e}")
        return []

# --- Streamlit UI ---

st.title("Автоматичен детектор на стойностни футболни залози с форма и head-to-head")

max_matches = st.sidebar.slider("Максимален брой мачове за форма и H2H", min_value=3, max_value=10, value=5)

st.info("Зареждане на мачове и коефициенти... Моля изчакайте.")

value_bets = []

for league_key, league_name in EURO_LEAGUES.items():
    st.header(f"Лига: {league_name}")
    matches = get_matches_from_odds_api(league_key)
    if not matches:
        st.write("Няма мачове или грешка при зареждане.")
        continue
    
    count_value = 0
    for match in matches:
        teams = match.get('teams', [])
        if len(teams) != 2:
            continue
        home_team, away_team = teams

        # Взимаме коефициенти за h2h пазара
        markets = match.get('bookmakers', [])
        bookmakers_count = len(markets)
        if bookmakers_count == 0:
            continue
        
        # Взимаме коефициенти от първия букмейкър (може да добавим логика за ликвидност)
        odds_h2h = None
        for bookmaker in markets:
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'].lower() == home_team.lower():
                            odds_h2h = outcome['price']
                            break
            if odds_h2h:
                break
        if not odds_h2h:
            continue
        
        # Вземаме форма и h2h статистика от flashscore
        form_home = calculate_form_strength(get_team_form(home_team, max_matches), home_team)
        h2h_strength = 0.5  # Ако искаш можеш да изчислиш по-точно с get_head_to_head
        
        est_prob, value = combined_probability(form_home, h2h_strength, odds_h2h)

        if value > 0:
            count_value += 1
            value_bets.append({
                'league': league_name,
                'home': home_team,
                'away': away_team,
                'odds_home_win': odds_h2h,
                'estimated_prob': est_prob,
                'value': value,
                'bookmakers': bookmakers_count,
            })

    st.write(f"Намерени стойностни залози: {count_value}")

if value_bets:
    st.subheader("Всички стойностни залози:")
    for bet in value_bets:
        st.markdown(f"**{bet['league']}**: {bet['home']} срещу {bet['away']}")
        st.write(f"Коефициент за победа на {bet['home']}: {bet['odds_home_win']}")
        st.write(f"Комбинирана вероятност: {bet['estimated_prob']:.2f}")
        st.write(f"Value на залога: {bet['value']:.3f}")
        st.write(f"Налични букмейкъри: {bet['bookmakers']}")
        st.write("---")
else:
    st.write("Не са намерени стойностни залози към момента.")
