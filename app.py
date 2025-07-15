import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Данни – реални прогнози с обосновки
def get_real_predictions():
    return [
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Elfsborg - Molde", "Прогноза": "ГГ", "Коеф": 1.85, "Сума": 20, "Резултат": "✅ Печеливш",
         "Обосновка": "И двата отбора показват висока резултатност, а Molde бележи средно над 1.5 гола като гост."},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "AIK - Kalmar", "Прогноза": "1", "Коеф": 1.75, "Сума": 30, "Резултат": "✅ Печеливш",
         "Обосновка": "AIK е силен домакин и се намира във възход, докато Kalmar е в слаба форма и с кадрови проблеми."},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Avai - Coritiba", "Прогноза": "1", "Коеф": 2.00, "Сума": 20, "Резултат": "❌ Губещ",
         "Обосновка": "Avai запазва стабилност у дома и има добър баланс срещу Coritiba."},

        {"Дата": str(date.today()), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се",
         "Обосновка": "И двата отбора играят дефанзивно в евротурнирите, очаква се предпазлив подход."},
        {"Дата": str(date.today()), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се",
         "Обосновка": "Malmo играе офанзивно у дома, а Saburtalo допуска голове почти във всеки мач."},
        {"Дата": str(date.today()), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се",
         "Обосновка": "Уругвай е в по-добра форма и има психологическо предимство след предишни победи."}
    ]

# Функция за изчисляване на банка
def calculate_bank(df, initial_bank):
    bank = initial_bank
    for _, row in df.iterrows():
        if row["Резултат"].startswith("✅"):
            bank += row["Сума"] * row["Коеф"] - row["Сума"]
        elif row["Резултат"].startswith("❌"):
            bank -= row["Сума"]
    return bank

# Функция за оцветяване на редове според резултата
def highlight_result(row):
    if row["Резултат"].startswith("✅"):
        return ['background-color: #d4edda'] * len(row)
    elif row["Резултат"].startswith("❌"):
        return ['background-color: #f8d7da'] * len(row)
    else:
        return [''] * len(row)

# Инициализация
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 340

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(get_real_predictions())

df = st.session_state.df

st.title("⚽ Прогнози и обосновки")

# Изчисляване на текуща банка и запис в сесия
st.session_state.bank = calculate_bank(df, st.session_state.initial_bank)

# Показване на банка
st.subheader("💰 Банка")
st.metric("Текущ баланс", f"{st.session_state.bank:.2f} лв")

# Показване на таблицата с прогнози, оцветена според резултат
st.subheader("📋 Всички прогнози")
df_styled = df.style.apply(highlight_result, axis=1)
st.dataframe(df_styled, use_container_width=True)

# Избор на мач за детайлна обосновка
st.subheader("🔎 Виж обосновка по мач")

match_options = [f"{row['Дата']} | {row['Мач']}" for _, row in df.iterrows()]
selected = st.selectbox("Избери мач", match_options)

selected_row = df.iloc[match_options.index(selected)]

with st.expander(f"🧠 Обосновка за {selected_row['Мач']}"):
    st.markdown(f"""
    - 📅 Дата: {selected_row['Дата']}
    - 🎯 Прогноза: **{selected_row['Прогноза']}**
    - 💸 Коефициент: {selected_row['Коеф']}
    - 💰 Залог: {selected_row['Сума']} лв
    - 📈 Резултат: {selected_row['Резултат']}
    - 📊 Обосновка:
    > {selected_row['Обосновка']}
    """)
