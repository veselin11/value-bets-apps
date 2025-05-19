import streamlit as st
import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
SPORTS_URL = "https://api.the-odds-api.com/v4/sports"
BASE_ODDS_URL = "https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

st.set_page_config(page_title="Футболни коефициенти", layout="wide")
st.title("Футболни събития с филтри")

@st.cache_data(show_spinner=False)
def get_soccer_leagues():
    resp = requests.get(SPORTS_URL, params={"apiKey": API_KEY})
    resp.raise_for_status()
    sports = resp.json()
    return [
        {"key": s["key"], "title": s["title"]}
        for s in sports if s["group"] == "Soccer" and s["active"]
    ]

@st.cache_data(show_spinner=False)
def get_odds_for_league(sport_key):
    url = BASE_ODDS_URL.format(sport_key=sport_key)
    params = {
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "apiKey": API_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

# 1. Зареждане на лиги
with st.spinner("Зареждане на футболни лиги..."):
    leagues = get_soccer_leagues()

league_keys = [l["key"] for l in leagues]
league_titles = {l["key"]: l["title"] for l in leagues}

# 2. Избор на лига
selected_leagues = st.multiselect(
    "Избери първенства", options=league_keys,
    format_func=lambda x: league_titles[x],
    default=league_keys[:3]  # първите 3 по подразбиране
)

all_matches = []
for league_key in selected_leagues:
    matches = get_odds_for_league(league_key)
    all_matches.extend(matches)

# 3. Извличане на всички букмейкъри от данните
bookmaker_set = set()
for match in all_matches:
    for bm in match.get("bookmakers", []):
        bookmaker_set.add(bm["title"])
bookmaker_list = sorted(bookmaker_set)

# 4. Филтър по букмейкър
selected_bookmakers = st.multiselect(
    "Избери букмейкъри", options=bookmaker_list, default=bookmaker_list
)

# 5. Показване на събития
for match in all_matches:
    show_match = False
    for bm in match.get("bookmakers", []):
        if bm["title"] in selected_bookmakers:
            show_match = True
    if not show_match:
        continue

    st.subheader(f"{match['home_team']} vs {match['away_team']}")
    st.caption(f"Лига: {league_titles.get(match['sport_key'], match['sport_key'])} | Начало: {match['commence_time']}")

    for bookmaker in match.get("bookmakers", []):
        if bookmaker["title"] not in selected_bookmakers:
            continue
        st.markdown(f"**{bookmaker['title']}**")
        for market in bookmaker.get("markets", []):
            if market["key"] == "h2h":
                outcomes = market["outcomes"]
                st.write({o["name"]: o["price"] for o in outcomes})
    st.markdown("---")
