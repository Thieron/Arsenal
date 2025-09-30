import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}
CURRENT_SEASON = 2025 


def get_team_id(team_name):
    """Retrieves the team ID from the API based on a search string."""
    url = f"{BASE_URL}/teams?search={team_name}"
    try:
        response = requests.get(url, headers=HEADERS).json()
        if not response["response"]:
            print(f"Warning: Team '{team_name}' not found by API search.")
            return None
        return response["response"][0]["team"]["id"]
    except requests.exceptions.RequestException as e:
        print(f"API Request Error for team ID: {e}")
        return None
    except KeyError:
        print("API Response structure unexpected for team ID.")
        return None

def get_last_fixtures(team_id, n=5):
    """Retrieves the last N fixtures for a given team and season."""
    url = f"{BASE_URL}/fixtures?team={team_id}&season={CURRENT_SEASON}&last={n}"
    try:
        response = requests.get(url, headers=HEADERS).json()
        return response["response"]
    except requests.exceptions.RequestException as e:
        print(f"API Request Error for last fixtures: {e}")
        return []
    except KeyError:
        print("API Response structure unexpected for last fixtures.")
        return []

def calculate_form_points(fixtures, team_id):
    """Calculates form points (3 for win, 1 for draw) from fixture data."""
    points = 0
    for match in fixtures:
        home_team_id = match["teams"]["home"]["id"]
        home_goals = match["score"]["fulltime"]["home"]
        away_goals = match["score"]["fulltime"]["away"]
        
        if home_goals is None or away_goals is None:
            continue
            
        if home_team_id == team_id: 
            # Team is Home
            if home_goals > away_goals:
                points += 3 # Win
            elif home_goals == away_goals:
                points += 1 # Draw
        else:
            # Team is Away
            if away_goals > home_goals:
                points += 3 # Win
            elif away_goals == home_goals:
                points += 1 # Draw
                
    return points

def get_seasonal_stats(team_name):
    """
    Hardcoded 2025/2026 Premier League statistics (Arsenal vs West Ham scenario)
    Data Format: (Position, Goals Scored, Goals Conceded, Matches Played)
    """
    stats = {
        "Arsenal": (2, 12, 3, 6),     
        "West Ham": (19, 5, 13, 5),   
    }
    return stats.get(team_name, (10, 0, 0, 0)) 


def predict_match_outcome(home_team_name, away_team_name, home_form_points, away_form_points):
    """
    Combines seasonal stats, home advantage, and short-term form for a weighted prediction.
    """
    home_score_base = 0
    away_score_base = 0
    
    home_pos, home_gs, home_gc, home_mp = get_seasonal_stats(home_team_name)
    away_pos, away_gs, away_gc, away_mp = get_seasonal_stats(away_team_name)

    # 1. HOME ADVANTAGE 
    HOME_ADVANTAGE_POINTS = 2.0
    home_score_base += HOME_ADVANTAGE_POINTS
    
    # Positional Points 
    home_pos_points = 3.0 if home_pos <= 4 else 2.0 if home_pos <= 8 else 1.0 if home_pos <= 17 else 0.0
    away_pos_points = 3.0 if away_pos <= 4 else 2.0 if away_pos <= 8 else 1.0 if away_pos <= 17 else 0.0
    home_score_base += home_pos_points
    away_score_base += away_pos_points
    
    # Goals Difference Ratio 
    home_gd_ratio = (home_gs - home_gc) / max(1, home_mp)
    away_gd_ratio = (away_gs - away_gc) / max(1, away_mp)
    home_score_base += home_gd_ratio * 1.5
    away_score_base += away_gd_ratio * 1.5

    # 3. SHORT-TERM FORM
    home_score_base += home_form_points * 0.3
    away_score_base += away_form_points * 0.3

    home_score_base += 0.5 

    away_score_base += 0.0 
    
    differential_score = home_score_base - away_score_base


    if differential_score >= 3.0:
        return f"**{home_team_name} Win (Comfortable Victory)**: Overwhelming statistical dominance, positional strength, and home advantage secure a clear win.", (3, 0), differential_score
    elif differential_score > 0.5:
        return f"**{home_team_name} Win (Solid Performance)**: Superior seasonal form and home advantage tip the balance. A hard-fought win is the most likely result.", (2, 1), differential_score
    elif differential_score >= -0.5:
        return f"**Draw (Score Line Likely 1-1)**: The seasonal gaps are closely offset by the opponent's recent form or intangible boosts, resulting in a tightly contested draw.", (1, 1), differential_score
    else:
        return f"**{away_team_name} Win (Major Upset)**: The home side's form is poor enough to be overcome by the opponent, leading to a shock defeat.", (0, 1), differential_score

if __name__ == "__main__":
    home_team_name = input("Enter Home Team: ") or "Arsenal"
    away_team_name = input("Enter Away Team: ") or "West Ham"

    home_id = get_team_id(home_team_name)
    away_id = get_team_id(away_team_name)

    if not home_id or not away_id:
        print("Could not retrieve team IDs. Check team names or API key.")
    else:
        home_form = get_last_fixtures(home_id)
        away_form = get_last_fixtures(away_id)
        
        home_points = calculate_form_points(home_form, home_id)
        away_points = calculate_form_points(away_form, away_id)

        prediction_text, score_line, differential = predict_match_outcome(
            home_team_name, away_team_name, home_points, away_points
        )

        # --- Output ---
        print("\n" + "="*50)
        print("            🔮 MATCH PREDICTION & ANALYSIS")
        print("="*50)
        print(f"Fixture: {home_team_name} vs {away_team_name}")
        

        h_pos, h_gs, h_gc, h_mp = get_seasonal_stats(home_team_name)
        a_pos, a_gs, a_gc, a_mp = get_seasonal_stats(away_team_name)

        print("\n--- 📈 Data Used in Calculation ---")
        print(f"-> {home_team_name} Seasonal (Pos/GS/GC/MP): {h_pos}th / {h_gs} / {h_gc} / {h_mp}")
        print(f"-> {away_team_name} Seasonal (Pos/GS/GC/MP): {a_pos}th / {a_gs} / {a_gc} / {a_mp}")
        print(f"-> {home_team_name} Form (Last 5 points): {home_points}")
        print(f"-> {away_team_name} Form (Last 5 points): {away_points}")

        print("\n--- 🧠 Prediction Breakdown ---")
        print(f"Total Prediction Differential Score: **{differential:+.1f}**")
        print(prediction_text)
        
        print(f"\nFinal Score Prediction: **{home_team_name} {score_line[0]} - {score_line[1]} {away_team_name}**")
        print("="*50)