import streamlit as st
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt

# Фиксирани реални прогнози от ChatGPT (можеш да добавяш още)
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

# Инициализация
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 340

if 'bets' not in st.session_state:
    st.session_state.bets = []

# Интерфейс
st.title("📊 Архив и статистика на прогнози")

# Зареждане на реалните прогнози
if st.button("🔄 Зареди новите прогнози"):
    new_preds = get_chatgpt_predictions()
    st.session_state.bets = new_preds  # Презаписваме
    st.success("Прогнозите са презаредени!")

# Показване на таблицата с оцветяване
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)

    def highlight_result(row):
        if row['Резултат'] == "✅ Печеливш":
            return ['background-color: #e6ffe6'] * len(row)
        elif row['Резултат'] == "❌ Губещ":
            return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Архив на всички прогнози")
    st.dataframe(df.style.apply(highlight_result, axis=1), use_container_width=True)

    # Изчисляване на дневни стойности на банката
    bank = st.session_state.initial_bank
    history = []
    for i, row in df.iterrows():
        result = row['Резултат']
        amount = row['Сума']
        coef = row['Коеф']
        if result == "✅ Печеливш":
            win = amount * coef
            bank += win - amount
        elif result == "❌ Губещ":
            bank -= amount
        history.append({"Дата": row['Дата'], "Банка": round(bank, 2)})

    # Показване на графика
    st.subheader("📈 Графика на движението на банката")
    chart_df = pd.DataFrame(history)
    chart_df['Дата'] = pd.to_datetime(chart_df['Дата'])
    chart_df = chart_df.sort_values("Дата")
    st.line_chart(chart_df.set_index("Дата")["Банка"])

    # Финална метрика
    st.subheader("💰 Актуална банка")
    st.metric("Баланс", f"{bank:.2f} лв")

else:
    st.info("Натисни бутона, за да заредиш прогнозите.")
