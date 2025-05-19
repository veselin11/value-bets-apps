import streamlit as st
import requests
from datetime import datetime
import pytz

team_form_cache = {}

ODDS_API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
API_FOOTBALL_KEY = "cb4a5917231d8b20dd6b85ae9d025e6e"

PRIMARY_BOOKMAKER = "pinnacle"
MIN_VALUE_THRESHOLD = 1.20

st.title("Стойностни залози чрез сравнение с Pinnacle")

def get_team_form(team_name):
    if team_name in team_form_cache:
        return team_form_cache[team_name]
    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    r = requests.get(url, headers=headers)
    try:
        team_id = r.json()['response'][0]['team']['id']
        form_url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024&league=1"
        form_response = requests.get(form_url, headers=headers)
        form_str = form_response.json().get("response", {}).get("form", "")
        form_score = form_str.count("W") / len(form_str) if form_str else 0.5
    except:
        form_score = 0.5
    team_form_cache[team_name] = form_score
    return form_score

def calculate_probabilities(home, away):
    form_home = get_team_form(home)
    form_away = get_team_form(away)
    prob_home = round(0.4 + (form_home - form_away) * 0.3, 2)
    prob_away = round(0.4 + (form_away - form_home) * 0.3, 2)
    prob_draw = round(1 - prob_home - prob_away, 2)
    return max(min(prob_home, 0.85), 0.05), max(min(prob_draw, 0.85), 0.05), max(min(prob_away, 0.85), 0.05)

def is_value_bet(prob, odds):
    return round(prob * odds, 2) >= MIN_VALUE_THRESHOLD

params = {
    "regions": "eu",
    "markets": "h2h",
    "oddsFormat": "decimal",
    "apiKey": ODDS_API_KEY
}
url = "https://api.the-odds-api.com/v4/sports/soccer/odds"

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    matches = response.json()
    st.write(f"Общо заредени мачове: {len(matches)}")

    all_bets = []

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        commence = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00')).astimezone(pytz.timezone("Europe/Sofia"))

        bookmakers = match.get("bookmakers", [])
        pinnacle_market = next((b for b in bookmakers if b['key'] == PRIMARY_BOOKMAKER), None)
        if not pinnacle_market:
            continue

        pin_odds = {o['name']: o['price'] for o in pinnacle_market['markets'][0]['outcomes']}
        prob_home, prob_draw, prob_away = calculate_probabilities(home, away)

        for bookmaker in bookmakers:
            if bookmaker['key'] == PRIMARY_BOOKMAKER:
                continue

            market = bookmaker['markets'][0]
            for outcome in market['outcomes']:
                team = outcome['name']
                odds = outcome['price']
                pin_price = pin_odds.get(team)
                if pin_price and odds > pin_price:
                    diff = round(odds - pin_price, 2)
                    if team == home:
                        prob = prob_home
                    elif team == away:
                        prob = prob_away
                    else:
                        prob = prob_draw
                    value = round(prob * odds, 2)

                    all_bets.append({
                        "match": f"{home} vs {away}",
                        "start": commence.strftime('%Y-%m-%d %H:%M'),
                        "bookmaker": bookmaker['key'],
                        "team": team,
                        "odds": odds,
                        "pinnacle": pin_price,
                        "diff": diff,
                        "prob": prob,
                        "value": value
                    })

    sorted_bets = sorted(all_bets, key=lambda x: x["value"], reverse=True)

    for bet in sorted_bets:
        st.subheader(f"{bet['match']} ({bet['start']})")
        st.markdown(f"- **{bet['team']}** при **{bet['bookmaker']}**: {bet['odds']} | Pinnacle: {bet['pinnacle']} | Разлика: **+{bet['diff']}**")
        st.markdown(f"  → Вероятност: {bet['prob']}, Стойност: {bet['value']}")

        if bet['value'] >= MIN_VALUE_THRESHOLD:
            st.markdown(f"<span style='color:green'><b>→ Стойностен залог!</b></span>", unsafe_allow_html=True)
        elif bet['value'] >= 1.0:
            st.markdown(f"<span style='color:gray'>→ Средна стойност</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>→ Ниска стойност</span>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Грешка при зареждане: {e}")
