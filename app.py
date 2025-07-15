import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --- Функция с актуални прогнози (вчера и днес)
def load_current_predictions():
    return [
        # Вчерашни мачове (с реални резултати)
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Elfsborg - Molde", "Прогноза": "ГГ", "Коеф": 1.85, "Сума": 20, "Резултат": "✅ Печеливш",
         "Обосновка": "И двата отбора показват висока резултатност, а Molde бележи средно над 1.5 гола като гост."},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "AIK - Kalmar", "Прогноза": "1", "Коеф": 1.75, "Сума": 30, "Резултат": "✅ Печеливш",
         "Обосновка": "AIK е силен домакин и се намира във възход, докато Kalmar е в слаба форма и с кадрови проблеми."},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Avai - Coritiba", "Прогноза": "1", "Коеф": 2.00, "Сума": 20, "Резултат": "❌ Губещ",
         "Обосновка": "Avai запазва стабилност у дома и има добър баланс срещу Coritiba."},

        # Днешни мачове (очаква се)
        {"Дата": str(date.today()), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се",
         "Обосновка": "И двата отбора играят дефанзивно в евротурнирите, очаква се предпазлив подход."},
        {"Дата": str(date.today()), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се",
         "Обосновка": "Malmo играе офанзивно у дома, а Saburtalo допуска голове почти във всеки мач."},
        {"Дата": str(date.today()), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се",
         "Обосновка": "Уругвай е в по-добра форма и има психологическо предимство след предишни победи."},
    ]

# --- Инициализация състояния
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 340

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(load_current_predictions())

df = st.session_state.df

st.title("📊 Прогнози за спортни залози")

# --- Пресмятане на банка
bank = st.session_state.initial_bank
for _, row in df.iterrows():
    if row["Резултат"] == "✅ Печеливш":
        bank += row["Сума"] * row["Коеф"] - row["Сума"]
    elif row["Резултат"] == "❌ Губещ":
        bank -= row["Сума"]

st.subheader("💰 Текущ баланс")
st.metric("Банка", f"{bank:.2f} лв")

# --- Показване таблица без "Обосновка"
cols_for_table = ["Дата", "Мач", "Прогноза", "Коеф", "Сума", "Резултат"]
st.subheader("🎯 Прогнози")
st.dataframe(df[cols_for_table], use_container_width=True)

# --- Избор мач за обосновка
st.subheader("🔎 Обосновка на мач")
match_options = [f"{row['Дата']} | {row['Мач']}" for _, row in df.iterrows()]
selected = st.selectbox("Избери мач", match_options)
selected_row = df.iloc[match_options.index(selected)]

st.markdown(f"""
### 🧠 Обосновка за **{selected_row['Мач']}**
- 📅 Дата: {selected_row['Дата']}
- 🎯 Прогноза: **{selected_row['Прогноза']}**
- 💸 Коеф.: {selected_row['Коеф']}
- 💰 Сума: {selected_row['Сума']} лв
- 📈 Резултат: {selected_row['Резултат']}
- 📊 Обосновка:
> {selected_row['Обосновка']}
""")
