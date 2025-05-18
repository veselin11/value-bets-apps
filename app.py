import streamlit as st
import requests
from bs4 import BeautifulSoup

def parse_team_form(team_name):
    # Примерен парсинг от flashscore (работи ако URL е достъпен)
    team_slug = team_name.lower().replace(' ', '-')
    url = f"https://www.flashscore.com/team/{team_slug}/results/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        results_div = soup.find_all('div', class_='event__result')
        form = []
        for res in results_div[:5]:
            text = res.text.strip()
            if '-' in text:
                home_goals, away_goals = text.split('-')
                home_goals, away_goals = int(home_goals), int(away_goals)
                # За пример винаги приемаме, че търсим резултата за домакин (прецизирай по нужда)
                if home_goals > away_goals:
                    form.append('W')
                elif home_goals == away_goals:
                    form.append('D')
                else:
                    form.append('L')
            else:
                form.append('U')
        return form
    except Exception as e:
        st.warning(f"Грешка при зареждане на форма за {team_name}: {e}")
        return []

def parse_head_to_head(home, away):
    # Тук ще използваме фиктивни данни или същия метод за парсинг
    # Вариант: да се добави реален парсинг от flashscore / друг сайт по-късно
    return {
        'matches_played': 5,
        'home_wins': 2,
        'away_wins': 1,
        'draws': 2
    }

def main():
    st.title("Автоматичен детектор на стойностни футболни залози с форма и H2H")

    # Тук зареждаш мачове и коефициенти от The Odds API - пример:
    matches = [
        {'home': 'Manchester United', 'away': 'Liverpool', 'markets': {'1X2': {'home_win': 2.4, 'draw': 3.3, 'away_win': 2.8}}},
        # Добави реални мачове тук
    ]

    for match in matches:
        st.subheader(f"{match['home']} vs {match['away']}")

        home_form = parse_team_form(match['home'])
        away_form = parse_team_form(match['away'])
        h2h = parse_head_to_head(match['home'], match['away'])

        st.write(f"Форма {match['home']}: {' '.join(home_form)}")
        st.write(f"Форма {match['away']}: {' '.join(away_form)}")
        st.write(f"H2H статистика: Игри: {h2h['matches_played']}, Победи домакин: {h2h['home_wins']}, Победи гост: {h2h['away_wins']}, Равенства: {h2h['draws']}")

        # Логика за изчисляване на вероятности и стойностни залози
        # Пример (опростено):
        # Ако домакинът е в по-добра форма и по-добър H2H резултат -> препоръка за победа на домакин

        if home_form.count('W') > away_form.count('W') and h2h['home_wins'] > h2h['away_wins']:
            st.success(f"Препоръка: Залог за победа на {match['home']} с коеф. {match['markets']['1X2']['home_win']}")
        else:
            st.info("Няма ясна стойностна препоръка.")

if __name__ == "__main__":
    main()
