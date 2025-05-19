import streamlit as st
import requests

# Настройки
API_KEY_ODDS = "2e086a4b6d758dec878ee7b5593405b1"  # The Odds API ключ
API_FOOTBALL_KEY = "e004e3601abd4b108a653f9f3a8c5ede"  # API-Football ключ
INITIAL_BANK = 500
LEAGUE_ID = 39  # Premier League

# Статистика от API-Football
def get_team_form(team_name, league_id):
    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    if not data["response"]:
        return []
    team_id = data["response"][0]["team"]["id"]

    fixtures_url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&league={league_id}&last=5"
    fixtures_res = requests.get(fixtures_url, headers=headers)
    fixtures = fixtures_res.json().get("response", [])
    results = []
    for match in fixtures:
        winner = match["teams"]["home"]["name"] if match["teams"]["home"]["winner"] else match["teams"]["away"]["name"] if match["teams"]["away"]["winner"] else "Draw"
        if winner == team_name:
            results.append("W")
        elif winner == "Draw":
            results.append("D")
        else:
            results.append("L")
    return results

def calculate_win_probability(form):
    wins = form.count("W")
    draws = form.count("D")
    losses = form.count("L")
    total = max(wins + draws + losses, 1)
    return round(wins / total, 2), round(draws / total, 2), round(losses / total, 2)

def implied_prob(odds):
    return round(1 / odds, 2) if odds > 0 else 0

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    params = {
        "apiKey": API_KEY_ODDS,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

# Основна логика
def find_value_bets(matches):
    bets = []
    for match in matches:
        teams = match.get("teams")
        if not teams:
            continue
        team1 = teams.get("home")
        team2 = teams.get("away")
        if not team1 or not team2:
            continue

        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            continue

        outcomes = bookmakers[0]["markets"][0]["outcomes"]
        odds_dict = {o["name"]: o["price"] for o in outcomes}

        form1 = get_team_form(team1, LEAGUE_ID)
        form2 = get_team_form(team2, LEAGUE_ID)

        win1, _, _ = calculate_win_probability(form1)
        win2, _, _ = calculate_win_probability(form2)
        draw_prob = 1 - (win1 + win2)

        for outcome, odd in odds_dict.items():
            market_prob = implied_prob(odd)
            if outcome == team1:
                value = win1 - market_prob
            elif outcome == team2:
                value = win2 - market_prob
            else:
                value = draw_prob - market_prob

            if value > 0.05:
                bet_amount = round((value * INITIAL_BANK) / 10, 2)
                bets.append({
                    "match": f"{team1} vs {team2}",
                    "selection": outcome,
                    "odds": odd,
                    "value": round(value, 2),
                    "stake": bet_amount
                })
    return bets

# Streamlit UI
st.set_page_config(page_title="Стойностни залози", layout="centered")
st.title("Стойностни футболни залози (1X2) с реална статистика")

matches = fetch_odds()
if matches:
    st.success(f"Намерени срещи: {len(matches)}")
    value_bets = find_value_bets(matches)
    if value_bets:
        for bet in value_bets:
            st.subheader(bet["match"])
            st.write(f"- **Избор:** {bet['selection']}")
            st.write(f"- **Коефициент:** {bet['odds']}")
            st.write(f"- **Стойност:** {bet['value']}")
            st.write(f"- **Препоръчителен залог:** {bet['stake']} лв")
            st.markdown("---")
    else:
        st.warning("Няма стойностни залози в момента.")
else:
    st.error("Грешка при зареждане на мачове.")
