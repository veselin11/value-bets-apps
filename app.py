import streamlit as st
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

# -- Примерни реални прогнози
def load_predictions():
    return [
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Bodo/Glimt - Ruzomberok", "Прогноза": "1", "Коеф": 1.55, "Сума": 20, "Резултат": "2:0", "Статус": "Печели", "Обосновка": "Bodo е с по-силен състав и домакинството е решаващо."},
        {"Дата": str(date.today() - timedelta(days=1)), "Мач": "Avaí - Ceará", "Прогноза": "ГГ", "Коеф": 1.95, "Сума": 20, "Резултат": "0:1", "Статус": "Губи", "Обосновка": "И двата отбора често бележат. Очаква се размяна на голове."},
        {"Дата": str(date.today()), "Мач": "Kairat - Olimpija", "Прогноза": "Под 2.5", "Коеф": 1.65, "Сума": 40, "Резултат": "Очаква се", "Статус": "", "Обосновка": "Два дефанзивни отбора. Малко голове в последните им срещи."},
        {"Дата": str(date.today()), "Мач": "Malmo - Saburtalo", "Прогноза": "Над 2.5", "Коеф": 1.60, "Сума": 20, "Резултат": "Очаква се", "Статус": "", "Обосновка": "Malmo бележи много у дома, Saburtalo допуска голове."},
        {"Дата": str(date.today()), "Мач": "Uruguay W - Argentina W", "Прогноза": "1", "Коеф": 2.00, "Сума": 10, "Резултат": "Очаква се", "Статус": "", "Обосновка": "Uruguay е в по-добра форма и домакинството е предимство."},
    ]

# -- Инициализация
if 'bank' not in st.session_state:
    st.session_state.bank = 340
if 'predictions' not in st.session_state:
    st.session_state.predictions = load_predictions()

st.title("📊 Прогнози за спортни залози")
st.subheader("🎯 Таблица с прогнози")

df = pd.DataFrame(st.session_state.predictions)

# -- JavaScript стил за колона "Статус"
cell_style_jscode = JsCode("""
function(params) {
    if (params.value === 'Печели') {
        return {backgroundColor: '#d4f7dc'};
    } else if (params.value === 'Губи') {
        return {backgroundColor: '#fddddd'};
    } else {
        return {};
    }
}
""")

# -- Конфигуриране на таблицата
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection("single")
gb.configure_columns(["Дата", "Мач", "Прогноза", "Коеф", "Сума", "Резултат", "Статус"], editable=False)
gb.configure_column("Статус", cellStyle=cell_style_jscode)
grid_options = gb.build()

response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    height=300,
    fit_columns_on_grid_load=True
)

# -- Обосновка
selected = response['selected_rows']
if selected:
    match = selected[0]
    st.markdown("---")
    st.subheader(f"📌 Обосновка за мача: {match['Мач']}")
    st.info(match['Обосновка'])

# -- История на печалби и графика
st.subheader("📈 История на печалби")
df['Печалба'] = df.apply(lambda row: (row['Коеф'] * row['Сума'] - row['Сума']) if row['Статус'] == 'Печели' else (-row['Сума'] if row['Статус'] == 'Губи' else 0), axis=1)
df['Натрупана банка'] = st.session_state.bank + df['Печалба'].cumsum()

fig, ax = plt.subplots()
ax.plot(df['Дата'], df['Натрупана банка'], marker='o', linestyle='-')
ax.set_title("Движение на банката")
ax.set_ylabel("Лева")
ax.set_xlabel("Дата")
st.pyplot(fig)

# -- Финална банка
st.subheader("💰 Актуална банка")
bank_total = st.session_state.bank + df['Печалба'].sum()
st.metric("Текуща банка", f"{bank_total:.2f} лв")
