import streamlit as st
from datetime import datetime

# --- ДАННИ ЗА ПРОГНОЗИ (пример) ---
matches = [
    {
        "match": "Sirius vs Mjällby",
        "date": "2025-07-14",
        "predictions": {
            "1X2": {"Pick": "1", "Odds": 1.90, "Analysis": "Mjällby са по-силният отбор и фаворит."},
            "Goals": {"Pick": "Over 2.5", "Odds": 3.60, "Analysis": "Прогнозираме открит мач с голове."},
            "BTTS": {"Pick": "No", "Odds": 1.50, "Analysis": "Sirius трудно вкарват на чужд терен."}
        }
    },
    # Можем да добавим още мачове...
]

# --- Streamlit интерфейс ---
st.set_page_config(page_title="ProBet - Твоите спортни прогнози", layout="wide")

st.title("ProBet – Уникални спортни прогнози и анализи")

st.markdown("## Прогнози за днес – " + datetime.today().strftime('%Y-%m-%d'))

for match_data in matches:
    if match_data["date"] == datetime.today().strftime('%Y-%m-%d'):
        st.subheader(match_data["match"])
        
        with st.expander("Прогнози и анализ"):
            preds = match_data["predictions"]
            for bet_type, info in preds.items():
                st.markdown(f"**{bet_type}**: `{info['Pick']}` | Коефициент: {info['Odds']}")
                st.write(info["Analysis"])
        
        # Опция за залог
        st.markdown("### Постави залог")
        bet_choice = st.selectbox(f"Избери залог за {match_data['match']}", options=list(preds.keys()))
        bet_amount = st.number_input(f"Сума за залог на {bet_choice}", min_value=10, max_value=300, step=10, value=20)
        
        if st.button(f"Пусни залог: {match_data['match']} - {bet_choice} за {bet_amount} лв"):
            st.success(f"Залогът ти за {bet_choice} на {match_data['match']} е приет! Успех!")

st.markdown("---")
st.write("© 2025 ProBet. Всички права запазени.")
