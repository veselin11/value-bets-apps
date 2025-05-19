import streamlit as st
import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

@st.cache_data(ttl=3600)
def get_active_soccer_leagues():
    url = "https://api.the-odds-api.com/v4/sports"
    params = {"apiKey": API_KEY}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    sports = response.json()
    active_soccer = [
        s for s in sports if "soccer" in s["key"] and s["active"]
    ]
    return active_soccer

# Заглавие в приложението
st.subheader("Активни футболни лиги с налични мачове днес")

# Зареждане и показване
leagues = get_active_soccer_leagues()
if leagues:
    for league in leagues:
        st.markdown(f"- **{league['title']}** (`{league['key']}`)")
else:
    st.info("Няма активни лиги в момента или възникна грешка при зареждане.")
