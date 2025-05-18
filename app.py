import streamlit as st
import random
import datetime

# Настройки
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 500
if 'bets_history' not in st.session_state:
    st.session_state.bets_history = []
if 'todays_matches' not in st.session_state:
    st.session_state.todays_matches = [
        {"match": "Барселона vs Хетафе", "odds": 1.55, "prediction": "1", "selected": False},
        {"match": "Верона vs Болоня", "odds": 2.10, "prediction": "2", "selected": False},
        {"match": "Брюж vs Андерлехт", "odds": 2.45, "prediction": "X", "selected": False},
        {"match": "Славия София vs Локомотив Пловдив", "odds": 1.95, "prediction": "1", "selected": False}
    ]

today = datetime.date.today()

st.title("Приложение за стойностни залози - Футбол")
st.write(f"Текуща банка: {st.session_state.bankroll:.2f} лв.")

st.subheader("Днешни мачове")
for i, match in enumerate(st.session_state.todays_matches):
    selected = st.checkbox(f"{match['match']} | Прогноза: {match['prediction']} | Коефициент: {match['odds']}", key=i)
    st.session_state.todays_matches[i]['selected'] = selected

bet_amount = st.number_input("Въведи сума за залог на избран мач:", min_value=1, max_value=st.session_state.bankroll, value=50)

def place_bet(match_index, amount):
    match = st.session_state.todays_matches[match_index]
    if not match["selected"]:
        st.warning(f"Не си избрал мача: {match['match']}")
        return
    if match.get("bet_placed", False):
        st.warning(f"Вече си заложил на мача: {match['match']}")
        return

    # Симулиране на резултат по вероятност, базирана на коефициента (по-голям коефициент -> по-ниска вероятност за успех)
    win_prob = 1 / match["odds"]
    win = random.random() < win_prob

    if win:
        profit = amount * (match["odds"] - 1)
        st.session_state.bankroll += profit
        result = "Печалба"
    else:
        st.session_state.bankroll -= amount
        result = "Загуба"

    match["bet_placed"] = True

    st.session_state.bets_history.append({
        "match": match["match"],
        "prediction": match["prediction"],
        "odds": match["odds"],
        "amount": amount,
        "result": result,
        "date": str(today)
    })

    st.success(f"{match['match']} | Прогноза: {match['prediction']} | Коефициент: {match['odds']} | {result} | Банка: {st.session_state.bankroll:.2f} лв.")

if st.button("Заложи на избраните мачове"):
    any_selected = False
    for i, match in enumerate(st.session_state.todays_matches):
        if match['selected'] and not match.get("bet_placed", False):
            if bet_amount <= st.session_state.bankroll:
                place_bet(i, bet_amount)
                any_selected = True
            else:
                st.error("Нямаш достатъчно пари в банката за този залог.")
                break
    if not any_selected:
        st.info("Моля, избери поне един мач и натисни бутона за залог.")

st.subheader("История на залозите")
if st.session_state.bets_history:
    for bet in st.session_state.bets_history:
        st.write(f"{bet['date']} | {bet['match']} | Прогноза: {bet['prediction']} | Коефициент: {bet['odds']} | {bet['result']} | Залог: {bet['amount']} лв.")
else:
    st.write("Все още няма направени залози.")

# Автоматичен подбор на стойностни залози
st.subheader("Автоматичен подбор на стойностни залози")

def is_value_bet(odds, win_prob_estimate):
    return odds > 1 / win_prob_estimate

# Примерни оценки за вероятности (можеш да развиеш с по-точни модели)
prob_estimates = {
    "Барселона vs Хетафе": 0.7,
    "Верона vs Болоня": 0.4,
    "Брюж vs Андерлехт": 0.42,
    "Славия София vs Локомотив Пловдив": 0.5
}

value_bets = []
for match in st.session_state.todays_matches:
    est = prob_estimates.get(match['match'], 0.5)
    if is_value_bet(match['odds'], est):
        value_bets.append(match)

if value_bets:
    st.write("Предложения за стойностни залози:")
    for vb in value_bets:
        st.write(f"- {vb['match']} | Коефициент: {vb['odds']} | Прогноза: {vb['prediction']}")
else:
    st.write("Няма ясни стойностни залози за днес.")
