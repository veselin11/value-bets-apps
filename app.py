import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Стойностни Залози", layout="wide")
st.title("Най-стойностни футболни залози за деня")

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
BOOKMAKER_PRIORITY = ["matchbook", "betfair", "unibet"]
PINNACLE_KEY = "pinnacle"

MIN_VALUE_THRESHOLD = 1.05
MIN_PROBABILITY_THRESHOLD = 0.55

@st.cache_data(ttl=600)
def get_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer_europe_all/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    return response.json()

def estimate_probability(bookmaker_odds: dict):
    odds_list = [o for o in bookmaker_odds.values() if o > 1.01]
    if len(odds_list) < 2:
        return 0
    avg = sum(1 / o for o in odds_list) / len(odds_list)
    return min(0.99, 1 / avg)

def calculate_value(probability, odds):
    return probability * odds

def format_team_names(name):
    return name.replace(" FC", "").replace(" IF", "").replace(" 1903", "")

matches = get_odds()
st.subheader(f"Общо сканирани мачове: {len(matches)}")

shown = 0
for match in matches:
    home, away = match["home_team"], match["away_team"]
    commence = datetime.datetime.fromisoformat(match["commence_time"]).strftime("%Y-%m-%d %H:%M")

    pinnacle_odds = {}
    best_odds = {}

    for bookmaker in match["bookmakers"]:
        if bookmaker["key"] == PINNACLE_KEY:
            for market in bookmaker["markets"]:
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        pinnacle_odds[outcome["name"]] = outcome["price"]

        if bookmaker["key"] in BOOKMAKER_PRIORITY:
            for market in bookmaker["markets"]:
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        name = outcome["name"]
                        price = outcome["price"]
                        if name not in best_odds or price > best_odds[name]["price"]:
                            best_odds[name] = {"price": price, "bookmaker": bookmaker["key"]}

    for outcome, info in best_odds.items():
        if outcome in pinnacle_odds:
            our_prob = estimate_probability(pinnacle_odds)
            if our_prob < MIN_PROBABILITY_THRESHOLD:
                continue
            value = calculate_value(our_prob, info["price"])
            if value >= MIN_VALUE_THRESHOLD:
                st.markdown(f"**{format_team_names(home)} vs {format_team_names(away)} ({commence})**")
                st.write(f"{outcome} при {info['bookmaker']}: {info['price']} | Pinnacle: {pinnacle_odds[outcome]:.2f} | Разлика: +{info['price'] - pinnacle_odds[outcome]:.2f}")
                st.success(f"→ Вероятност: {our_prob:.2f}, Стойност: {value:.2f} → Стойностен залог!")
                shown += 1

if shown == 0:
    st.warning("Няма стойностни залози с над 55% вероятност за момента.")
