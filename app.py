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

# Инициализация
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 340

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(get_real_predictions())

df = st.session_state.df

st.title("⚽ Прогнози и обосновки")

# Текуща банка
bank = st.session_state.initial_bank
for _, row in df.iterrows():
    if row["Резултат"] == "✅ Печеливш":
        bank += row["Сума"] * row["Коеф"] - row["Сума"]
    elif row["Резултат"] == "❌ Губещ":
        bank -= row["Сума"]

st.subheader("💰 Банка")
st.metric("Текущ баланс", f"{bank:.2f} лв")

# Показване на всички прогнози
st.subheader("📋 Всички прогнози")
df_styled = df.style.apply(
    lambda row: ['background-color: #d4edda' if row["Резултат"].startswith("✅") else
                 'background-color: #f8d7da' if row["Резултат"].startswith("❌") else ''
                 for _ in row], axis=1)
st.dataframe(df_styled, use_container_width=True)

# Избор за детайлна обосновка
st.subheader("🔎 Виж обосновка по мач")

match_options = [f"{row['Дата']} | {row['Мач']}" for _, row in df.iterrows()]
selected = st.selectbox("Избери мач", match_options)

# Показване на обосновка
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
