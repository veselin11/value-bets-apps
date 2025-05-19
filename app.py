import streamlit as st
import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

leagues = [
    "soccer_bulgaria_pfl",
    "soccer_croatia_prva_hnl",
    "soccer_poland_ekstraklasa",
    "soccer_romania_liga_i",
]

regions = ["eu", "uk", "us"]
markets = ["h2h", "totals", "spreads"]

def fetch_odds(league, region, market):
    url = f"https://api.the-odds-api.com/v4/sports/{league}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": region,
        "markets": market,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Грешка при заявка: {league} | {region} | {market} -> {e}")
        return []

st.title("Проверка на мачове по лиги, региони и пазари")

for league in leagues:
    st.subheader(f"Лига: {league}")
    found_any = False
    for region in regions:
        for market in markets:
            matches = fetch_odds(league, region, market)
            if matches:
                found_any = True
                st.write(f"Регион: {region}, Пазар: {market}, Мачове: {len(matches)}")
                for match in matches:
                    teams = match.get("teams", [])
                    commence_time = match.get("commence_time", "unknown")
                    st.write(f" - {teams} | {commence_time}")
    if not found_any:
        st.info("Няма намерени мачове за тази лига.")
