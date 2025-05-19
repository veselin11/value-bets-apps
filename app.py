import streamlit as st
import requests
from datetime import datetime, timedelta

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"
SPORTS_URL = "https://api.the-odds-api.com/v4/sports"
BASE_ODDS_URL = "https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

st.set_page_config(page_title="Футболни събития", layout="wide")
st.title("Футболни мачове и коефициенти")

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

# 1. Филтър по дата
today = datetime.utcnow().date()
selected_date = st.date_input("Избери дата", value=today)

# 2. Зареждане на футболни лиги
with st.spinner("Зареждане на футболни лиги..."):
    leagues = get_soccer_leagues()

league_keys = [l["key"] for l in leagues]
league_titles = {l["key"]: l["title"] for l in leagues}

# 3. Филтър по лиги
selected_leagues = st.multiselect(
    "Избери първенства", options=league_keys,
    format_func=lambda x: league_titles[x],
    default=league_keys[:3]
)

# 4. Зареждане на мачове
all_matches = []
for league_key in selected_leagues:
    matches = get_odds_for_league(league_key)
    # филтрираме само по избраната дата
    for m in matches:
        match_time = datetime.fromisoformat(m["commence_time"].replace("Z", "+00:00")).date()
        if match_time == selected_date:
            all_matches.append(m)

# 5. Филтър по букмейкъри
bookmaker_set = set()
for match in all_matches:
    for bm in match.get("bookmakers", []):
        bookmaker_set.add(bm["title"])
bookmaker_list = sorted(bookmaker_set)

selected_bookmakers = st.multiselect(
    "Избери букмейкъри", options=bookmaker_list, default=bookmaker_list
)

# 6. Показване на мачове
if not all_matches:
    st.info("Няма мачове за избраната дата.")
else:
    for match in all_matches:
        home, away = match["home_team"], match["away_team"]
        start = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M UTC")

        st.markdown("### " + home + " vs " + away)
        st.caption(f"{league_titles.get(match['sport_key'], '')} | Начало: {start}")
        
        for bookmaker in match.get("bookmakers", []):
            if bookmaker["title"] not in selected_bookmakers:
                continue

            with st.expander(f"{bookmaker['title']}"):
                cols = st.columns(len(bookmaker["markets"][0]["outcomes"]))
                for i, outcome in enumerate(bookmaker["markets"][0]["outcomes"]):
                    cols[i].metric(label=outcome["name"], value=str(outcome["price"]))
        st.markdown("---")
