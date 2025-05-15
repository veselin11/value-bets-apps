import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="РЎС‚РѕР№РЅРѕСЃС‚РЅРё Р·Р°Р»РѕР·Рё", layout="wide")
st.title("РЎС‚РѕР№РЅРѕСЃС‚РЅРё Р·Р°Р»РѕР·Рё - РџСЂРµРјР°С‡")

API_KEY = "a3d6004cbbb4d16e86e2837c27e465d8"
SPORT = "soccer_epl"
REGION = "eu"
MARKET = "h2h"

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?regions={REGION}&markets={MARKET}&apiKey={API_KEY}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if not data:
            st.warning("РќСЏРјР° РЅР°Р»РёС‡РЅРё РїСЂРѕРіРЅРѕР·Рё РІ РјРѕРјРµРЅС‚Р°.")
        else:
            rows = []
            for match in data:
                teams = match['teams']
                commence_time = match['commence_time']
                for bookmaker in match['bookmakers']:
                    for market in bookmaker['markets']:
                        if market['key'] == 'h2h':
                            outcomes = market['outcomes']
                            row = {
                                "РњР°С‡": f"{teams[0]} - {teams[1]}",
                                "Р§Р°СЃ": commence_time,
                                "Р‘СѓРєРјРµР№РєСЉСЂ": bookmaker['title']
                            }
                            for outcome in outcomes:
                                row[outcome['name']] = outcome['price']
                            rows.append(row)
            df = pd.DataFrame(rows)
            st.dataframe(df)
    else:
        st.error(f"Р“СЂРµС€РєР° РїСЂРё Р·Р°СЏРІРєР°С‚Р°: {response.status_code}")
        st.json(response.json())
except Exception as e:
    st.error(f"Р“СЂРµС€РєР° РїСЂРё Р·Р°СЂРµР¶РґР°РЅРµ: {e}")
