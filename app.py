import streamlit as st
import pandas as pd
from datetime import date, timedelta

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
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "CSKA - Levski", "Прогноза": "1", "Коеф": 2.20, "Сума": 30, "Резултат": "✅ Печеливш"},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Ludogorets - Botev", "Прогноза": "Под 2.5", "Коеф": 1.80, "Сума": 20, "Резултат": "❌ Губещ"},
    ]

# Заглавие
st.title("⚽ Автоматични прогнози")

# Зареждане на мачовете
if st.button("🔄 Зареди мачовете за днес"):
    auto_bets = get_auto_predictions()
    st.session_state.bets.extend(auto_bets)
    st.success("Мачовете са заредени!")

# История на прогнозите
st.subheader("📋 Прогнози от днес и вчера")

if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)
    df_filtered = df[df['Дата'].isin([str(date.today()), str(date.today() - timedelta(days=1))])]

    def highlight_result(row):
        if row['Резултат'] == "✅ Печеливш":
            return ['background-color: #e6ffe6'] * len(row)
        elif row['Резултат'] == "❌ Губещ":
            return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)

    st.dataframe(df_filtered.style.apply(highlight_result, axis=1), use_container_width=True)

    # Актуализирай банката въз основа на завършили мачове
    total_profit = 0
    for bet in st.session_state.bets:
        if bet["Резултат"] == "✅ Печеливш":
            total_profit += bet["Сума"] * bet["Коеф"] - bet["Сума"]
        elif bet["Резултат"] == "❌ Губещ":
            total_profit -= bet["Сума"]
    st.session_state.bank = 340 + total_profit
else:
    st.info("Няма прогнози.")

# Банка
st.subheader("💰 Актуална банка")
st.metric("Остатък", f"{st.session_state.bank:.2f} лв")
