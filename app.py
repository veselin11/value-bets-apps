import streamlit as st
import pandas as pd
from datetime import date

# Инициализация на сесия
if 'bank' not in st.session_state:
    st.session_state.bank = 340  # текуща банка след последния ден

if 'bets' not in st.session_state:
    st.session_state.bets = []

st.title("🎯 Спортни прогнози – Тракер")
st.write("Следи прогнозите, печалбите и развитието на банката")

# Форма за нова прогноза
st.subheader("➕ Добави прогноза")
with st.form("add_bet"):
    match = st.text_input("Мач")
    prediction = st.selectbox("Прогноза", ["1", "X", "2", "Под 2.5", "Над 2.5", "ГГ", "Няма ГГ"])
    odds = st.number_input("Коефициент", min_value=1.01, value=1.50, step=0.01)
    stake = st.number_input("Сума на залог (лв)", min_value=10, step=10)
    result = st.selectbox("Резултат", ["Очаква се", "✅ Печеливш", "❌ Губещ"])
    submit = st.form_submit_button("Добави")

    if submit:
        st.session_state.bets.append({
            "Дата": str(date.today()),
            "Мач": match,
            "Прогноза": prediction,
            "Коеф": odds,
            "Сума": stake,
            "Резултат": result
        })

        if result == "✅ Печеливш":
            st.session_state.bank += stake * odds - stake
        elif result == "❌ Губещ":
            st.session_state.bank -= stake

# Показване на всички прогнози
st.subheader("📋 История на прогнозите")
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Все още няма добавени прогнози.")

# Текуща банка
st.subheader("💰 Актуална банка")
st.metric("Остатък", f"{st.session_state.bank:.2f} лв")
