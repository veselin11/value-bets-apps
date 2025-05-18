# value_bets_detector.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import math
import re

# === Настройки на API ===
ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
FOOTBALL_DATA_API_KEY = "e004e3601abd4b108a653f9f3a8c5ede"

# === Помощни функции ===
def implied_probability(odds):
    return 1 / odds if odds > 0 else 0

def value_bet_check(prob, odds):
    return prob > implied_probability(odds)

def kelly_criterion(prob, odds):
    return ((prob * (odds - 1)) - (1 - prob)) / (odds - 1)

# === Извличане на Flashscore линкове ===
def search_flashscore_team_url(team_name):
    search_url = f"https://www.flashscore.com/search/?q={team_name.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        if "/team/" in a["href"]:
            return "https://www.flashscore.com" + a["href"]
    return None

def get_team_form(flashscore_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(flashscore_url + "results/", headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        form = []
        for result in soup.select(".event__match--static")[:5]:
            if "event__match--won" in result["class"]:
                form.append("W")
            elif "event__match--draw" in result["class"]:
                form.append("D")
            elif "event__match--lost" in result["class"]:
                form.append("L")
        return form
    except:
        return []

def calculate_form_score(form):
    score = 0
    for f in form:
        if f == "W": score += 3
        elif f == "D": score += 1
    return score / (len(form) * 3) if form else 0.5

# === Зареждане на коефициенти от Odds API ===
def load_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h,totals",
        "oddsFormat": "decimal"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        st.error(f"Грешка при зареждане на коефициенти: {r.status_code} - {r.text}")
        return []
    return r.json()

# === Основно приложение ===
def main():
    st.title("Автоматичен детектор на стойностни футболни залози с форма и H2H")

    with st.spinner("Зареждане на мачове и коефициенти..."):
        odds_data = load_odds()

    if not odds_data:
        st.warning("Няма налични мачове.")
        return

    for match in odds_data:
        home_team = match['home_team']
        away_team = match['away_team']
        bookmakers = match.get('bookmakers', [])

        if not bookmakers:
            continue

        bookie = bookmakers[0]
        markets = {m['key']: m for m in bookie['markets']}
        odds_h2h = {o['name']: o['price'] for o in markets.get('h2h', {}).get('outcomes', [])}
        odds_totals = markets.get('totals', {}).get('outcomes', [])

        # Зареждане на форма
        home_url = search_flashscore_team_url(home_team)
        away_url = search_flashscore_team_url(away_team)
        home_form = get_team_form(home_url) if home_url else []
        away_form = get_team_form(away_url) if away_url else []

        form_home_score = calculate_form_score(home_form)
        form_away_score = calculate_form_score(away_form)

        st.subheader(f"{home_team} vs {away_team}")
        st.write(f"Форма {home_team}: {'-'.join(home_form)} ({form_home_score:.2f})")
        st.write(f"Форма {away_team}: {'-'.join(away_form)} ({form_away_score:.2f})")

        # Оценка 1X2
        total = form_home_score + form_away_score
        prob_home = form_home_score / total if total else 0.5
        prob_away = form_away_score / total if total else 0.5

        if 'home' in odds_h2h:
            odds_home = odds_h2h['home']
            if value_bet_check(prob_home, odds_home):
                st.success(f"✅ Стойностен залог: Победа за {home_team} @ {odds_home:.2f}")

        if 'away' in odds_h2h:
            odds_away = odds_h2h['away']
            if value_bet_check(prob_away, odds_away):
                st.success(f"✅ Стойностен залог: Победа за {away_team} @ {odds_away:.2f}")

        st.markdown("---")

if __name__ == '__main__':
    main()
