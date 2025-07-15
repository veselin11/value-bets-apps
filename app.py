import streamlit as st
import pandas as pd
from datetime import date, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Реални прогнози с обосновки
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

st.title("⚽ Прогнози и анализ")

# Актуална банка
bank = st.session_state.initial_bank
for _, row in df.iterrows():
    if row["Резултат"].startswith("✅"):
        bank += row["Сума"] * row["Коеф"] - row["Сума"]
    elif row["Резултат"].startswith("❌"):
        bank -= row["Сума"]

st.subheader("💰 Банка")
st.metric("Текущ баланс", f"{bank:.2f} лв")

# Настройки за AgGrid
gb = GridOptionsBuilder.from_dataframe(df[["Дата", "Мач", "Прогноза", "Коеф", "Сума", "Резултат"]])
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

# Стилове според резултата
cell_style_jscode = """
function(params) {
    if (params.value.includes("Печеливш")) {
        return { 'backgroundColor': '#d4edda' };
    } else if (params.value.includes("Губещ")) {
        return { 'backgroundColor': '#f8d7da' };
    }
    return {};
}
"""

# Добавяме стила към колоната "Резултат"
gb.configure_column("Резултат", cellStyle=cell_style_jscode)
grid_options = gb.build()

st.subheader("📋 Прогнози")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True
)

selected = grid_response['selected_rows']

# Показване на обосновка при избор
if selected:
    row = selected[0]
    st.subheader(f"🧠 Обосновка за {row['Мач']}")
    st.markdown(f"""
    - 📅 Дата: {row['Дата']}
    - 🎯 Прогноза: **{row['Прогноза']}**
    - 💸 Коефициент: {row['Коеф']}
    - 💰 Залог: {row['Сума']} лв
    - 📈 Резултат: {row['Резултат']}
    - 📊 Обосновка:
    > {row['Обосновка']}
    """)
else:
    st.info("Избери мач от таблицата, за да видиш подробна обосновка.")
