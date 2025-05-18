import streamlit as st
import random
import datetime
import matplotlib.pyplot as plt

# Инициализация на сесията
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 500.0
if 'bets_history' not in st.session_state:
    st.session_state.bets_history = []
if 'todays_matches' not in st.session_state:
    st.session_state.todays_matches = [
        {"id": 1, "match": "Барселона vs Хетафе", "odds": 1.55, "prediction": "1", "league": "Ла Лига", "date": str(datetime.date.today()), "selected": False, "marked": False},
        {"id": 2, "match": "Верона vs Болоня", "odds": 2.10, "prediction": "2", "league": "Серия А", "date": str(datetime.date.today()), "selected": False, "marked": False},
        {"id": 3, "match": "Брюж vs Андерлехт", "odds": 2.45, "prediction": "X", "league": "Белгийска Лига", "date": str(datetime.date.today()), "selected": False, "marked": False},
        {"id": 4, "match": "Славия София vs Локомотив Пловдив", "odds": 2.00, "prediction": "1", "league": "България", "date": str(datetime.date.today()), "selected": False, "marked": False}
    ]

st.title("🔮 Най-доброто приложение за залози")

# Банка
st.markdown(f"### 💰 Текуща банка: {st.session_state.bankroll:.2f} лв.")

# Филтриране на мачове
st.sidebar.header("Филтри")
all_leagues = sorted(set(m['league'] for m in st.session_state.todays_matches))
selected_league = st.sidebar.selectbox("Избери лига", ["Всички"] + all_leagues)
min_odds = st.sidebar.slider("Минимален коефициент", 1.0, 5.0, 1.0, 0.05)
show_marked = st.sidebar.checkbox("Покажи само маркирани мачове", False)

# Филтриране по критерии
filtered = st.session_state.todays_matches
if selected_league != "Всички":
    filtered = [m for m in filtered if m["league"] == selected_league]
filtered = [m for m in filtered if m["odds"] >= min_odds]
if show_marked:
    filtered = [m for m in filtered if m["marked"]]

st.subheader("Днешни мачове")

for match in filtered:
    cols = st.columns([3, 1, 1, 1, 1])
    cols[0].write(f"**{match['match']}** ({match['league']}) - Прогноза: {match['prediction']} | Коефициент: {match['odds']}")
    # Маркирай мач
    marked = cols[1].checkbox("⭐", value=match["marked"], key=f"mark_{match['id']}")
    match["marked"] = marked

    if not match["selected"]:
        amount = cols[2].number_input(f"Залог (лв.)", min_value=1, max_value=int(st.session_state.bankroll), value=50, key=f"bet_amount_{match['id']}")
        prediction = cols[3].selectbox("Прогноза", options=["1", "X", "2"], index=["1","X","2"].index(match["prediction"]), key=f"pred_{match['id']}")

        if cols[4].button("Заложи", key=f"bet_btn_{match['id']}"):
            if amount > st.session_state.bankroll:
                st.warning("Недостатъчно средства!")
            else:
                # Симулиране на резултат (за тест)
                win = random.random() < 1 / match["odds"]
                result = "Печалба" if win else "Загуба"
                if win:
                    profit = amount * (match["odds"] - 1)
                    st.session_state.bankroll += profit
                else:
                    st.session_state.bankroll -= amount

                match["selected"] = True
                match["prediction"] = prediction

                st.session_state.bets_history.append({
                    "id": match["id"],
                    "match": match["match"],
                    "prediction": prediction,
                    "odds": match["odds"],
                    "amount": amount,
                    "result": result,
                    "date": str(datetime.date.today())
                })
                st.success(f"{match['match']} - {result}! Текуща банка: {st.session_state.bankroll:.2f} лв.")

    else:
        st.write("⚠️ Вече заложен")

# Отмяна на залог преди игра
st.subheader("Управление на залози")
if st.session_state.bets_history:
    for bet in st.session_state.bets_history:
        cancel = st.button(f"Отмени залог: {bet['match']} ({bet['amount']} лв.)", key=f"cancel_{bet['id']}")
        if cancel:
            # Възстановяване на банка само ако още няма резултат (тук приемаме, че има)
            st.session_state.bankroll += bet['amount'] if bet['result'] == "Загуба" else 0
            # Премахване на залога
            st.session_state.bets_history = [b for b in st.session_state.bets_history if b['id'] != bet['id']]
            for m in st.session_state.todays_matches:
                if m['id'] == bet['id']:
                    m['selected'] = False
            st.experimental_rerun()
else:
    st.write("Все още няма заложени мачове.")

# Статистика
st.subheader("📊 Статистика на залозите")

total_bets = len(st.session_state.bets_history)
wins = sum(1 for bet in st.session_state.bets_history if bet['result'] == "Печалба")
losses = total_bets - wins
profit = st.session_state.bankroll - 500

st.write(f"- Общо залози: {total_bets}")
st.write(f"- Печалби: {wins}")
st.write(f"- Загуби: {losses}")
st.write(f"- Обща печалба/загуба: {profit:.2f} лв.")

# Графика на печалбата/загубата във времето
st.subheader("Графика на банката във времето")

dates = []
banks = []
current_bank = 500.0
dates.append(datetime.date.today())
banks.append(current_bank)

for bet in st.session_state.bets_history:
    if bet['result'] == "Печалба":
        current_bank += bet['amount'] * (bet['odds'] - 1)
    else:
        current_bank -= bet['amount']
    dates.append(datetime.datetime.strptime(bet['date'], "%Y-%m-%d").date())
    banks.append(current_bank)

fig, ax = plt.subplots()
ax.plot(dates, banks, marker='o')
ax.set_xlabel("Дата")
ax.set_ylabel("Банка (лв.)")
ax.set_title("Промяна на банката във времето")
st.pyplot(fig)

# Автоматичен подбор на мачове с high value bets (примерно)
st.subheader("Автоматичен подбор на мачове (стойностни залози)")

def is_value_bet(odds, win_prob_estimate):
    # Ако коефициентът е по-голям от обратната вероятност = value bet
    return odds > 1 / win_prob_estimate

# Примерни win_prob_estimates (можеш да подобриш с ML/статистика)
prob_estimates = {
    "Барселона vs Хетафе": 0.7,
    "Верона vs Болоня": 0.4,
    "Брюж vs
