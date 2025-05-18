import streamlit as st
import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_team_form(team_name, max_matches=5):
    search_url = f"https://www.flashscore.com/search/?q={team_name.replace(' ', '%20')}"
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    team_link = None
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/team/' in href:
            team_link = "https://www.flashscore.com" + href
            break
    if not team_link:
        return []
    team_resp = requests.get(team_link, headers=HEADERS)
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

def get_head_to_head(team1, team2, max_matches=5):
    t1 = team1.lower().replace(' ', '-')
    t2 = team2.lower().replace(' ', '-')
    h2h_url = f"https://www.flashscore.com/match-up/{t1}-{t2}/"
    resp = requests.get(h2h_url, headers=HEADERS)
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

def calculate_h2h_strength(matches, team_name):
    return calculate_form_strength(matches, team_name)

def combined_probability(form_strength, h2h_strength, odds):
    estimated_prob = 0.6 * form_strength + 0.4 * h2h_strength
    implied_prob = 1 / odds if odds > 0 else 0
    value = estimated_prob - implied_prob
    return estimated_prob, value

def bookmaker_liquidity_count(bookmakers_list):
    return len(bookmakers_list) if bookmakers_list else 0

# --- Streamlit UI ---

st.title("Стойностни футболни залози с форма и head-to-head")

team1 = st.text_input("Отбор 1 (например: Liverpool)")
team2 = st.text_input("Отбор 2 (например: Manchester City)")
odds = st.number_input("Коефициент за победа на Отбор 1", min_value=1.01, format="%.2f", step=0.01)

if st.button("Изчисли стойностен залог"):
    if not team1 or not team2:
        st.error("Моля въведете и двата отбора.")
    elif odds <= 1.0:
        st.error("Коефициентът трябва да е по-голям от 1.0")
    else:
        with st.spinner("Извличане на данни..."):
            form_matches = get_team_form(team1)
            h2h_matches = get_head_to_head(team1, team2)
            form_strength = calculate_form_strength(form_matches, team1)
            h2h_strength = calculate_h2h_strength(h2h_matches, team1)
            est_prob, value = combined_probability(form_strength, h2h_strength, odds)
        
        st.markdown(f"**Форма на {team1}:** {form_strength:.2f}")
        st.markdown(f"**Head-to-head сила на {team1} срещу {team2}:** {h2h_strength:.2f}")
        st.markdown(f"**Комбинирана вероятност:** {est_prob:.2f}")
        st.markdown(f"**Value на залога:** {value:.3f}")
        
        if value > 0:
            st.success("✅ Стойностен залог! 📈")
        else:
            st.warning("⚠️ Няма стойностен залог.")

        if form_matches:
            st.markdown(f"### Последни {len(form_matches)} мача на {team1}:")
            for m in form_matches:
                st.write(f"{m['date']}: {m['home']} {m['score']} {m['away']}")

        if h2h_matches:
            st.markdown(f"### Head-to-head последни {len(h2h_matches)} мача между {team1} и {team2}:")
            for m in h2h_matches:
                st.write(f"{m['date']}: {m['home']} {m['score']} {m['away']}")
