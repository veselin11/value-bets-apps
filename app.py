import streamlit as st
import pandas as pd
from datetime import date, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# Инициализация
if "bank" not in st.session_state:
    st.session_state.bank = 340

if "bets" not in st.session_state:
    # Добавяме примерни прогнози
    st.session_state.bets = [
        {
            "Дата": str(date.today() - timedelta(days=1)),
            "Мач": "Malmo - Saburtalo",
            "Прогноза": "Над 2.5",
            "Коеф": 1.60,
            "Сума": 20,
            "Резултат": "Печели",
            "Обосновка": "Malmo бележи много у дома. Saburtalo допуска поне 2 гола в 5 от последните 6 мача."
        },
        {
            "Дата": str(date.today() - timedelta(days=1)),
            "Мач": "Avaí - Amazonas",
            "Прогноза": "1",
            "Коеф": 2.30,
            "Сума": 20,
            "Резултат": "Губи",
            "Обосновка": "Avaí бяха в добра форма у дома, докато Amazonas са слаби гости."
        },
        {
            "Дата": str(date.today()),
            "Мач": "Kairat - Olimpija",
            "Прогноза": "Под 2.5",
            "Коеф": 1.65,
            "Сума": 40,
            "Резултат": "Очаква се",
            "Обосновка": "И двата отбора играят предпазливо в международни мачове. Малко голове в последните им срещи."
        },
    ]

# Заглавие
st.title("⚽ Прогнози и история на залозите")

# Данни
df = pd.DataFrame(st.session_state.bets)

# Стил за резултатите
cell_style = JsCode("""
function(params) {
    if (params.value === 'Печели') {
        return { 'backgroundColor': '#e0ffe0' }
    } else if (params.value === 'Губи') {
        return { 'backgroundColor': '#ffe0e0' }
    }
    return {};
}
""")

# Grid опции
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Резултат", cellStyle=cell_style)
gb.configure_selection(selection_mode="single", use_checkbox=False)
grid_options = gb.build()

# Таблица
st.subheader("📋 Таблица с прогнози")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False
)

# Обосновка при избор
selected = grid_response["selected_rows"]
if selected:
    st.subheader("📌 Обосновка за избран мач")
    st.markdown(f"**{selected[0]['Мач']}** — _{selected[0]['Дата']}_")
    st.write(selected[0]["Обосновка"])

# Банка
st.subheader("💰 Актуална банка")
bank = st.session_state.bank
st.metric("Остатък", f"{bank:.2f} лв")
