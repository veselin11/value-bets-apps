import streamlit as st import requests import pandas as pd import datetime

Заглавие на приложението

st.set_page_config(page_title="Стойностни Залози", layout="wide") st.title("Стойностни залози - Премачове")

Настройки

st.sidebar.header("Настройки") api_key = st.sidebar.text_input("API ключ", value="a3d6004cbbb4d16e86e2837c27e465d8") начална_банка = st.sidebar.number_input("Начална банка (лв)", min_value=0.0, value=500.0) целева_печалба = st.sidebar.number_input("Целева печалба (лв)", min_value=0.0, value=150.0) дни_за_постигане = st.sidebar.number_input("Брой дни за постигане на целта", min_value=1, value=5) мин_value = st.sidebar.slider("Минимален value %", 0.0, 100.0, 5.0, step=0.5)

Изчисляване на залога на база цел

дневна_печалба = целева_печалба / дни_за_постигане залог_на_мач = дневна_печалба

Заявка към API

url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?regions=eu&markets=h2h&apiKey={api_key}" try: response = requests.get(url) if response.status_code == 200: data = response.json() прогнози = [] for мач in data: отбори = мач['teams'] коефициенти = мач['bookmakers'][0]['markets'][0]['outcomes'] for коеф in коефициенти: вероятност = 1 / коеф['price'] implied = вероятност * 100 fair = 100 / sum([1 / o['price'] for o in коефициенти]) value = round((fair * implied) - 100, 2) if value >= мин_value: прогнози.append({ 'Събитие': f"{отбори[0]} vs {отбори[1]}", 'Залог': коеф['name'], 'Коефициент': коеф['price'], 'Value %': value, 'Залог (лв)': round(залог_на_мач, 2) })

if прогнози:
        df = pd.DataFrame(прогнози)
        df_sorted = df.sort_values(by="Value %", ascending=False)
        st.success(f"Намерени {len(df)} стойностни прогнози")
        st.dataframe(df_sorted)
    else:
        st.warning("Няма прогнози с достатъчно високо value %.")
elif response.status_code == 401:
    st.error("Грешка: API ключът не е валиден или са изчерпани заявките.")
else:
    st.error(f"Възникна грешка при заявката: {response.status_code}")

except Exception as e: st.error(f"Грешка при свързване с API: {e}")

Забележка за потребителя

st.markdown("""

Забележка: Това е тестова версия само с мачове от английската Висша лига (EPL). Скоро ще има избор на първенства. """)

