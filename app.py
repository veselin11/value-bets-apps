import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Твоите прогнози от вчера (датата е вчерашна)
yesterday = date.today() - timedelta(days=1)
today = date.today()

def get_predictions():
    return [
        # Вчерашни прогнози (твоите)
        {"Дата": str(yesterday), "Мач": "Sirius vs Mjällby (Allsvenskan, Швеция)", "Прогноза": "Победа Mjällby (1X2)", "Коеф": 1.95, "Сума": 40,
         "Резултат": "Очаква се",
         "Обосновка": "Mjällby са лидери в лигата, с отлична форма и най-добър гостуващ рекорд. Sirius са в лоша форма у дома, с 4 загуби в последните 6 мача."},
        
        {"Дата": str(yesterday), "Мач": "Sirius vs Mjällby", "Прогноза": "Над 2.5 гола", "Коеф": 1.60, "Сума": 20,
         "Резултат": "Очаква се",
         "Обосновка": "Mjällby открито вкарват голове, а Sirius често допускат вратата си – H2H има множество резултати над 3 гола."},
        
        {"Дата": str(yesterday), "Мач": "Athletic Club vs Avaí (Бразилия, Série B)", "Прогноза": "Победа Avaí (1X2)", "Коеф": 2.50, "Сума": 10,
         "Резултат": "Очаква се",
         "Обосновка": "Avaí има значителен превес спрямо слабата форма на Athletic Club, с CheckForm™ 6 срещу 0, позиция 4 срещу 20."},
        
        # Днешни прогнози (пример)
        {"Дата": str(today), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се",
         "Обосновка": "И двата отбора играят дефанзивно в евротурнирите, очаква се предпазлив подход."},
        {"Дата": str(today), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се",
         "Обосновка": "Malmo играе офанзивно у дома, а Saburtalo допуска голове почти във всеки мач."},
        {"Дата": str(today), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се",
         "Обосновка": "Уругвай е в по-добра форма и има психологическо предимство след предишни победи."}
    ]

# Инициализация
if 'initial_bank' not in st.session_state:
    st.session_state.initial_bank = 300  # стартова банка според обяснението ти

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(get_predictions())

df = st.session_state.df

st.title("⚽ Прогнози и обосновки")

# Банка
bank = st.session_state.initial_bank
for _, row in df.iterrows():
    if row["Резултат"] == "✅ Печеливш":
        bank += row["Сума"] * row["Коеф"] - row["Сума"]
    elif row["Резултат"] == "❌ Губещ":
        bank -= row["Сума"]

st.subheader("💰 Банка")
st.metric("Текущ баланс", f"{bank:.2f} лв")

# Таблица без колона "Обосновка"
cols_for_table = ["Дата", "Мач", "Прогноза", "Коеф", "Сума", "Резултат"]
st.subheader("📋 Прогнози")
st.dataframe(df[cols_for_table], use_container_width=True)

# Избор на мач за детайлна обосновка
st.subheader("🔎 Виж обосновка")
match_options = [f"{row['Дата']} | {row['Мач']}" for _, row in df.iterrows()]
selected = st.selectbox("Избери мач", match_options)
selected_row = df.iloc[match_options.index(selected)]

st.markdown(f"""
### 🧠 Обосновка за **{selected_row['Мач']}**
- 📅 Дата: {selected_row['Дата']}
- 🎯 Прогноза: **{selected_row['Прогноза']}**
- 💸 Коефициент: {selected_row['Коеф']}
- 💰 Сума: {selected_row['Сума']} лв
- 📈 Резултат: {selected_row['Резултат']}
- 📊 Обосновка:
> {selected_row['Обосновка']}
""")
