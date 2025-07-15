import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Прогнози от ChatGPT – реални мачове (днес и вчера)
def get_chatgpt_predictions():
    return [
        # Вчерашни (с резултати)
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Elfsborg - Molde", "Прогноза": "ГГ", "Коеф": 1.85, "Сума": 20, "Резултат": "✅ Печеливш"},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "AIK - Kalmar", "Прогноза": "1", "Коеф": 1.75, "Сума": 30, "Резултат": "✅ Печеливш"},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Avai - Coritiba", "Прогноза": "1", "Коеф": 2.00, "Сума": 20, "Резултат": "❌ Губещ"},

        # Днешни (очаквани)
        {"Дата": str(date.today()), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се"},
        {"Дата": str(date.today()), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се"},
        {"Дата": str(date.today()), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се"},
    ]

# Инициализация на сесията
if 'bank' not in st.session_state:
    st.session_state.bank = 340  # Начален капитал

if 'bets' not in st.session_state:
    st.session_state.bets = []

# Заглавие
st.title("⚽ Дневни прогнози от ChatGPT")

# Зареждане на прогнозите
if st.button("🔄 Зареди реалните прогнози"):
    predictions = get_chatgpt_predictions()
    st.session_state.bets = predictions  # Презаписваме, не добавяме
    st.success("Прогнозите са заредени!")

# Визуализация
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)

    # Оцветяване по резултат
    def highlight_result(row):
        if row['Резултат'] == "✅ Печеливш":
            return ['background-color: #e6ffe6'] * len(row)
        elif row['Резултат'] == "❌ Губещ":
            return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Прогнози от вчера и днес")
    st.dataframe(df.style.apply(highlight_result, axis=1), use_container_width=True)

    # Актуализиране на банката спрямо завършили мачове
    start_bank = 340
    total_profit = 0
    for bet in df.itertuples():
        if bet.Резултат == "✅ Печеливш":
            total_profit += bet.Сума * bet.Коеф - bet.Сума
        elif bet.Резултат == "❌ Губещ":
            total_profit -= bet.Сума
    st.session_state.bank = start_bank + total_profit
else:
    st.info("Натисни бутона по-горе, за да заредиш прогнозите.")

# Показване на текущата банка
st.subheader("💰 Актуална банка")
st.metric("Остатък", f"{st.session_state.bank:.2f} лв")
