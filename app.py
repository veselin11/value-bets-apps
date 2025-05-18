import streamlit as st
import random
import datetime

# Настройки
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 500
if 'bets_history' not in st.session_state:
    st.session_state.bets_history = []

# Днешна дата
today = datetime.date.today()

# Днешни мачове (примерни)
if 'todays_matches' not in st.session_state:
    st.session_state.todays_matches = [
        {"match": "Барселона vs Хетафе", "odds": 1.55, "prediction": "1", "selected": False},
        {"match": "Верона vs Болоня", "odds": 2.10, "prediction": "2", "selected": False},
        {"match": "Брюж vs Андерлехт", "odds": 2.45, "prediction": "X", "selected": False}
    ]

st.title("Приложение за залози")

st.write(f"**Текуща банка:** {st.session_state.bankroll:.2f} лв.")

st.write("---")
st.subheader("Днешни мачове")

def place_bet(match_index, amount):
    match = st.session_state.todays_matches[match_index]
    if match["selected"]:
        st.warning(f"Вече си заложил на мача: {match['match']}")
        return

    win = random.random() < 1 / match["odds"]
    result = "Печалба" if win else "Загуба"
    if win:
        profit = amount * (match["odds"] - 1)
        st.session_state.bankroll += profit
    else:
        st.session_state.bankroll -= amount

    match["selected"] = True
    st.session_state.bets_history.append({
        "match": match["match"],
        "prediction": match["prediction"],
        "odds": match["odds"],
        "amount": amount,
        "result": result,
        "date": str(today)
    })

    st.success(f"{match['match']} | Прогноза: {match['prediction']} | Коефициент: {match['odds']} | {result} | Банка: {st.session_state.bankroll:.2f} лв.")

# Показване на мачове с бутони за залог
for i, match in enumerate(st.session_state.todays_matches):
    st.write(f"**{match['match']}** | Прогноза: {match['prediction']} | Коефициент: {match['odds']}")
    if not match["selected"]:
        if st.button(f"Заложи 100 лв. на мач {i+1}"):
            place_bet(i, 100)

st.write("---")
st.subheader("История на залозите")
if st.session_state.bets_history:
    for bet in st.session_state.bets_history:
        st.write(f"{bet['date']} | {bet['match']} | {bet['prediction']} | {bet['odds']} | {bet['result']} | {bet['amount']} лв.")
else:
    st.write("Все още няма заложени мачове.")
