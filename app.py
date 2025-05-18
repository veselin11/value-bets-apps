import streamlit as st
import random
import datetime
import pandas as pd

# Стилове (същите като преди, можеш да ги копираш)

st.markdown(
    """
    <style>
    .main {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 20px;
    }
    .match-card {
        background: #1f1f1f;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6);
    }
    h1, h2 {
        color: #00bfa5;
        font-weight: 700;
    }
    div.stButton > button:first-child {
        background-color: #00bfa5;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 25px;
        transition: background-color 0.3s ease;
        border: none;
        box-shadow: 0 3px 6px rgba(0, 191, 165, 0.5);
    }
    div.stButton > button:first-child:hover {
        background-color: #008e76;
        cursor: pointer;
    }
    .stNumberInput > label {
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 6px;
        display: block;
    }
    .bet-history {
        background: #262626;
        border-radius: 10px;
        padding: 12px;
        margin-top: 20px;
        font-size: 14px;
        line-height: 1.4;
    }
    @media (max-width: 600px) {
        .main {
            padding: 10px;
        }
        div.stButton > button:first-child {
            width: 100%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Инициализация на сесията
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 500.0
if "bets_history" not in st.session_state:
    st.session_state.bets_history = []
if "todays_matches" not in st.session_state:
    st.session_state.todays_matches = [
        {"match": "Барселона vs Хетафе", "odds": 1.55, "prediction": "1", "selected": False},
        {"match": "Верона vs Болоня", "odds": 2.10, "prediction": "2", "selected": False},
        {"match": "Брюж vs Андерлехт", "odds": 2.45, "prediction": "X", "selected": False}
    ]

st.markdown('<div class="main">', unsafe_allow_html=True)

st.title("⚽ Стойностни залози - Управление на банка")

today = datetime.date.today()

st.subheader("Днешни мачове")

# Показване на мачове с "картички"
for i, match in enumerate(st.session_state.todays_matches):
    selected_text = "✅ Вече заложен" if match["selected"] else ""
    st.markdown(
        f'<div class="match-card"><b>{i + 1}. {match["match"]}</b><br>'
        f'Прогноза: {match["prediction"]} | Коефициент: {match["odds"]} {selected_text}</div>',
        unsafe_allow_html=True
    )

match_index = st.number_input(
    "Избери номер на мач за залог (0 за пропуск):",
    min_value=0,
    max_value=len(st.session_state.todays_matches),
    value=0,
    step=1
)

if match_index != 0:
    match_index -= 1
    match = st.session_state.todays_matches[match_index]

    if match["selected"]:
        st.warning(f"Вече си заложил на мача: {match['match']}")
    else:
        bet_amount = st.number_input(
            "Въведи сума за залог на избран мач:",
            min_value=1.0,
            max_value=float(st.session_state.bankroll),
            value=50.0,
            step=1.0,
            format="%.2f"
        )
        if st.button("Заложи"):
            win = random.random() < 1 / match["odds"]
            result = "Печалба" if win else "Загуба"
            if win:
                profit = bet_amount * (match["odds"] - 1)
                st.session_state.bankroll += profit
            else:
                st.session_state.bankroll -= bet_amount

            match["selected"] = True
            st.session_state.bets_history.append({
                "match": match["match"],
                "prediction": match["prediction"],
                "odds": match["odds"],
                "amount": bet_amount,
                "result": result,
                "date": str(today)
            })
            st.success(f"{match['match']} | {result}")
            st.info(f"Текуща банка: {st.session_state.bankroll:.2f} лв.")

# Филтър за историята
filter_opt = st.selectbox("Филтрирай залозите:", ["Всички", "Печеливши", "Загубени"])

history = st.session_state.bets_history

if filter_opt == "Печеливши":
    history = [bet for bet in history if bet["result"] == "Печалба"]
elif filter_opt == "Загубени":
    history = [bet for bet in history if bet["result"] == "Загуба"]

if history:
    st.subheader("История на залозите")
    for bet in reversed(history):
        color = "#4caf50" if bet["result"] == "Печалба" else "#f44336"
        st.markdown(
            f'<div class="bet-history" style="border-left: 5px solid {color};">'
            f"<b>{bet['date']}</b> | {bet['match']} | Прогноза: {bet['prediction']} | "
            f"Коефициент: {bet['odds']} | <span style='color:{color}'>{bet['result']}</span> | Залог: {bet['amount']:.2f} лв."
            f"</div>",
            unsafe_allow_html=True
        )
else:
    st.info("Все още няма залози по този филтър.")

# Статистика
st.subheader("Обобщена статистика")

total_bets = len(st.session_state.bets_history)
wins = len([b for b in st.session_state.bets_history if b["result"] == "Печалба"])
losses = len([b for b in st.session_state.bets_history if b["result"] == "Загуба"])
win_percent = (wins / total_bets * 100) if total_bets > 0 else 0
max_bet = max([b["amount"] for b in st.session_state.bets_history], default=0)
max_win = max(
    [b["amount"] * (b["odds"] - 1) for b in st.session_state.bets_history if b["result"] == "Печалба"],
    default=0
)

st.markdown(f"""
- Общо залози: **{total_bets}**
- Печаливши: **{wins}** ({win_percent:.1f}%)
- Загубени: **{losses}**
- Най-голям залог: **{max_bet:.2f} лв.**
- Най-голяма печалба: **{max_win:.2f} лв.**
""")

# Графика за печалби/загуби по дати
if total_bets > 0:
    df = pd.DataFrame(st.session_state.bets_history)
    df["date"] = pd.to_datetime(df["date"])
    df["profit"] = df.apply(
        lambda x: x["amount"] * (x["odds"] - 1) if x["result"] == "Печалба" else -x["amount"],
        axis=1
    )
    profit_by_date = df.groupby("date")["profit"].sum().cumsum()
    st.subheader("Натрупана печалба/загуба с времето")
    st.line_chart(profit_by_date)

st.markdown(f"<h3>Текуща банка
