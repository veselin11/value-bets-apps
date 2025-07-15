import streamlit as st
import pandas as pd
from datetime import date

# Инициализация
if 'bank' not in st.session_state:
    st.session_state.bank = 340

if 'bets' not in st.session_state:
    st.session_state.bets = []

# Примерни мачове с автоматични прогнози (вместо API)
def get_auto_predictions():
    return [
        {"Дата": str(date.today()), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се"},
        {"Дата": str(date.today()), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се"},
        {"Дата": str(date.today()), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се"},
    ]

# Бутон за автоматично добавяне
st.title("⚽ Автоматични прогнози за днес")
if st.button("🔄 Зареди мачовете за днес"):
    auto_bets = get_auto_predictions()
    st.session_state.bets.extend(auto_bets)
    st.success("Мачовете са заредени!")

# История
st.subheader("📋 История на прогнозите")
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Все още няма прогнози.")

# Банка
st.subheader("💰 Актуална банка")
st.metric("Остатък", f"{st.session_state.bank:.2f} лв")
