import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Прогнози с обосновка
def get_chatgpt_predictions():
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
if 'bets' not in st.session_state:
    st.session_state.bets = []

# Заглавие
st.title("🎯 Прогнози с обосновка и статистика")

# Зареждане на прогнози
if st.button("🔄 Зареди прогнозите"):
    st.session_state.bets = get_chatgpt_predictions()
    st.success("Прогнозите са заредени!")

# Архив с оцветяване
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)

    def highlight_result(row):
        if row['Резултат'] == "✅ Печеливш":
            return ['background-color: #e6ffe6'] * len(row)
        elif row['Резултат'] == "❌ Губещ":
            return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Архив на прогнозите")
    st.dataframe(df.drop("Обосновка", axis=1).style.apply(highlight_result, axis=1), use_container_width=True)

    # Избор на мач за обосновка
    st.subheader("🧠 Обосновка за избран мач")
    match_list = [f"{row.Дата} — {row.Мач}" for row in df.itertuples()]
    selected = st.selectbox("Избери мач", match_list)
    selected_index = match_list.index(selected)
    selected_row = df.iloc[selected_index]

    st.markdown(f"""
    ### 📌 {selected_row['Мач']}
    - 📅 Дата: {selected_row['Дата']}
    - 🎯 Прогноза: **{selected_row['Прогноза']}**
    - 💸 Коефициент: {selected_row['Коеф']}
    - 💰 Залог: {selected_row['Сума']} лв
    - 📊 Обосновка:
        > {selected_row['Обосновка']}
    """)

    # Актуална банка
    bank = st.session_state.initial_bank
    for _, row in df.iterrows():
        if row["Резултат"] == "✅ Печеливш":
            bank += row["Сума"] * row["Коеф"] - row["Сума"]
        elif row["Резултат"] == "❌ Губещ":
            bank -= row["Сума"]

    st.subheader("💰 Актуална банка")
    st.metric("Баланс", f"{bank:.2f} лв")

else:
    st.info("Натисни бутона, за да заредиш прогнозите.")
