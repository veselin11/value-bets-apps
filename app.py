import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Днешни прогнози, подготвени от ChatGPT
def get_today_predictions():
    today = str(date.today())
    return [
        {
            "Дата": today,
            "Мач": "Shamrock Rovers - Vikingur Reykjavik",
            "Прогноза": "Над 2.5",
            "Коеф": 1.87,
            "Сума": 30,
            "Резултат": "Очаква се",
            "Обосновка": "Shamrock имат 8 гола в последните 3 домакинства. Vikingur играят открито. Очаква се резултатен мач."
        },
        {
            "Дата": today,
            "Мач": "Ferencváros - The New Saints",
            "Прогноза": "Първо полувреме 1",
            "Коеф": 1.91,
            "Сума": 20,
            "Резултат": "Очаква се",
            "Обосновка": "Ferencváros повеждат рано в повечето домакинства. Гостите допускат голове в началото."
        },
        {
            "Дата": today,
            "Мач": "LDU Quito - Deportivo Cuenca",
            "Прогноза": "1 и Над 1.5",
            "Коеф": 2.10,
            "Сума": 20,
            "Резултат": "Очаква се",
            "Обосновка": "LDU силни у дома, много голове. Cuenca слаби навън, допускат средно по 2 гола."
        }
    ]

# Инициализация на банката и основната таблица
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 300

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame([])

# Заглавие и интерфейс
st.title("⚽ Прогнози и резултати")

# Бутон за зареждане на новите прогнози
if st.button("💡 Зареди днешните прогнози"):
    new_data = pd.DataFrame(get_today_predictions())
    st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)

# Актуализиране на банката
df = st.session_state.df
bank = st.session_state.initial_bank
for _, row in df.iterrows():
    if row["Резултат"] == "✅ Печеливш":
        bank += row["Сума"] * row["Коеф"] - row["Сума"]
    elif row["Резултат"] == "❌ Губещ":
        bank -= row["Сума"]

# Показване на текущата банка
st.subheader("💰 Банка")
st.metric("Текущ баланс", f"{bank:.2f} лв")

# Таблица с прогнози (без обосновка)
st.subheader("📋 Всички прогнози")
display_df = df.drop(columns=["Обосновка"])
df_styled = display_df.style.apply(
    lambda row: ['background-color: #d4edda' if row["Резултат"].startswith("✅") else
                 'background-color: #f8d7da' if row["Резултат"].startswith("❌") else ''
                 for _ in row], axis=1)
st.dataframe(df_styled, use_container_width=True)

# Детайлна обосновка при избор
st.subheader("🔎 Виж обосновка по мач")
if not df.empty:
    match_options = [f"{row['Дата']} | {row['Мач']}" for _, row in df.iterrows()]
    selected = st.selectbox("Избери мач", match_options)
    selected_row = df.iloc[match_options.index(selected)]
    st.markdown(f"""
    ### 🧠 Обосновка за **{selected_row['Мач']}**
    - 📅 Дата: {selected_row['Дата']}
    - 🎯 Прогноза: **{selected_row['Прогноза']}**
    - 💸 Коефициент: {selected_row['Коеф']}
    - 💰 Залог: {selected_row['Сума']} лв
    - 📈 Резултат: {selected_row['Резултат']}
    - 📊 Обосновка:
    > {selected_row['Обосновка']}
    """)
else:
    st.info("Няма заредени прогнози.")
