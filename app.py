import streamlit as st
import random
import datetime

# Настройки и състояние
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 500
if 'bets_history' not in st.session_state:
    st.session_state.bets_history = []
if 'todays_matches' not in st.session_state:
    st.session_state.todays_matches = [
        {"match": "Барселона vs Хетафе", "odds": 1.55, "prediction": "1", "league": "Ла Лига", "selected": False},
        {"match": "Верона vs Болоня", "odds": 2.10, "prediction": "2", "league": "Серия А", "selected": False},
        {"match": "Брюж vs Андерлехт", "odds": 2.45, "prediction": "X", "league": "Белгийска Лига", "selected": False},
        {"match": "Славия София vs Локомотив Пловдив", "odds": 2.00, "prediction": "1", "league": "България", "selected": False}
    ]

today = datetime.date.today()

st.title("Уникално приложение за залози")

st.write(f"**Текуща банка:** {st.session_state.bankroll:.2f} лв.")

# Филтриране по лига
all_leagues = sorted(set(m['league'] for m in st.session_state.todays_matches))
selected_league = st.selectbox("Филтрирай мачове по лига:", ["Всички"] + all_leagues)

if selected_league != "Всички":
    filtered_matches = [m for m in st.session_state.todays_matches if m['league'] == selected_league]
else:
    filtered_matches = st.session_state.todays_matches

# Филтриране по коефициент
min_odds = st.slider("Минимален коефициент:", 1.0, 5.0, 1.0, 0.05)
filtered_matches = [m for m in filtered_matches if m['odds'] >= min_odds]

st.subheader("Днешни мачове")
for i, match in enumerate(filtered_matches):
    st.markdown(f"**{match['match']}** ({match['league']}) - Прогноза: {match['prediction']} | Коефициент: {match['odds']}")
    if not match["selected"]:
        amount = st.number_input(f"Сума за залог на мач {i+1}:", min_value=1, max_value=int(st.session_state.bankroll), value=100, key=f"bet_amount_{i}")
        if st.button(f"Заложи на мач {i+1}", key=f"bet_btn_{i}"):
            if amount > st.session_state.bankroll:
                st.error("Нямаш достатъчно средства в банката!")
            else:
                # Симулиране на резултат
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

                st.success(f"{match['match']} | Резултат: {result} | Банка: {st.session_state.bankroll:.2f} лв.")

# Статистика
st.write("---")
st.subheader("Статистика")

total_bets = len(st.session_state.bets_history)
wins = sum(1 for bet in st.session_state.bets_history if bet['result'] == "Печалба")
losses = total_bets - wins
total_profit = st.session_state.bankroll - 500

st.write(f"Общо залози: {total_bets}")
st.write(f"Печалби: {wins}")
st.write(f"Загуби: {losses}")
st.write(f"Обща печалба/загуба: {total_profit:.2f} лв.")

st.write("---")
st.subheader("История на залозите")
if st.session_state.bets_history:
    for bet in st.session_state.bets_history:
        st.write(f"{bet['date']} | {bet['match']} | {bet['prediction']} | {bet['odds']} | {bet['result']} | {bet['amount']} лв.")
else:
    st.write("Все още няма заложени мачове.")
