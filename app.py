import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Примерни прогнози с обосновки, резултати и др.
data = [
    {
        "Date": "2025-07-15",
        "Match": "Kairat - Olimpija",
        "Prediction": "Под 2.5",
        "Odds": 1.65,
        "Stake": 40,
        "Result": "Win",
        "Reason": "Отборите играят стабилна защита, малко голове очакваме."
    },
    {
        "Date": "2025-07-15",
        "Match": "Malmo - Saburtalo",
        "Prediction": "Над 2.5",
        "Odds": 1.60,
        "Stake": 20,
        "Result": "Loss",
        "Reason": "Malmo има добър нападателен потенциал, но мачът излезе по-консервативен."
    },
    {
        "Date": "2025-07-15",
        "Match": "Uruguay W - Argentina W",
        "Prediction": "1",
        "Odds": 2.00,
        "Stake": 10,
        "Result": "Win",
        "Reason": "Уругвайки са в добра форма и домакинският фактор е силен."
    }
]

# Създаваме DataFrame и чистим обосновките
df = pd.DataFrame(data)
df["Reason"] = df["Reason"].fillna("").astype(str)

# JavaScript за оцветяване според резултата
cell_style_jscode = JsCode("""
function(params) {
    if (params.value === 'Win') {
        return {'backgroundColor': '#d4f7d4'};  // светло зелено
    } else if (params.value === 'Loss') {
        return {'backgroundColor': '#f7d4d4'};  // светло червено
    } else {
        return {};
    }
}
""")

st.title("Прогнози със залог и обосновка")

# Настройка на таблицата с AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Result", cellStyle=cell_style_jscode)
gb.configure_selection(selection_mode="single", use_checkbox=False)
grid_options = gb.build()

grid_response = AgGrid(df, gridOptions=grid_options, allow_unsafe_jscode=True, theme='material')

selected_rows = grid_response['selected_rows']

if selected_rows:
    selected = selected_rows[0]  # Първият (и единствен) избран ред
    st.subheader(f"Обосновка за мач: {selected['Match']}")
    st.write(selected['Reason'])
else:
    st.info("Изберете мач от таблицата, за да видите обосновката.")

# Показваме банка (пример)
if 'bank' not in st.session_state:
    st.session_state.bank = 340
st.subheader("Актуална банка")
st.metric("Остатък", f"{st.session_state.bank:.2f} лв")
