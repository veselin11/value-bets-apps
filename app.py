import requests

API_KEY = "2e086a4b6d758dec878ee7b5593405b1"

def get_soccer_sports():
    url = "https://api.the-odds-api.com/v4/sports"
    params = {"apiKey": API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    sports = response.json()

    soccer_sports = [sport for sport in sports if "soccer" in sport['key']]
    return soccer_sports

if __name__ == "__main__":
    soccer_sports = get_soccer_sports()
    print("Налични футболни спортове/лиги в The Odds API:")
    for sport in soccer_sports:
        print(f"{sport['key']} - {sport['title']}")
