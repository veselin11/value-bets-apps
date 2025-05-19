import streamlit as st
import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

def get_soccer_sports():
    url = "https://api.the-odds-api.com/v4/sports"
    params = {"apiKey": API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        sports = response.json()
        soccer_sports = [sport for sport in sports if "soccer" in sport['key']]
        return soccer_sports
    except Exception as e:
        st.error(f"Грешка при зареждане: {e}")
        return []

st.title("Футболни спортове и лиги")

soccer_sports = get_soccer_sports()
if soccer_sports:
    for sport in soccer_sports:
        st.write(f"{sport['key']} - {sport['title']}")
else:
    st.info("Няма намерени футболни спортове.")
