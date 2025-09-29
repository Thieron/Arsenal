import requests
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def get_team_id(team_name):
    url = f"{BASE_URL}/teams?search={team_name}"
    response = requests.get(url, headers=HEADERS).json()
    if not response["response"]:
        raise ValueError(f"Team '{team_name}' not found.")
    return response["response"][0]["team"]["id"]

def get_last_fixtures(team_id, n=5, season=2025):
    url = f"{BASE_URL}/fixtures?team={team_id}&season={season}&last={n}"
    response = requests.get(url, headers=HEADERS).json()
    return response["response"]

def calculate_form_points(fixtures, team_id):
    points = 0
    for match in fixtures:
        if match["teams"]["home"]["id"] == team_id:  
            if match["teams"]["home"]["winner"]:
                points += 3
            elif match["teams"]["home"]["winner"] is None:
                points += 1
        else:  # team is away
            if match["teams"]["away"]["winner"]:
                points += 3
            elif match["teams"]["away"]["winner"] is None:
                points += 1
    return points

# --- Main predictor ---
if __name__ == "__main__":
    home_team_name = input("Enter Home Team: ") or "Arsenal"
    away_team_name = input("Enter Away Team: ") or "West Ham"

    home_id = get_team_id(home_team_name)
    away_id = get_team_id(away_team_name)

    home_form = get_last_fixtures(home_id)
    away_form = get_last_fixtures(away_id)

    home_points = calculate_form_points(home_form, home_id)
    away_points = calculate_form_points(away_form, away_id)

    print("\n🔮 Match Prediction:")
    print(f"{home_team_name} vs {away_team_name}")
    print(f"{home_team_name} (last 5 games points): {home_points}")
    print(f"{away_team_name} (last 5 games points): {away_points}\n")

    if home_points > away_points + 2:
        prediction = f"✅ {home_team_name} is likely to win."
    elif away_points > home_points + 2:
        prediction = f"✅ {away_team_name} is likely to win."
    else:
        prediction = "🤝 Too close to call, could be a draw."

    print("Prediction:", prediction)