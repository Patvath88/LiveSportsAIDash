# backend/routers/predictions.py
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime, timezone
import xgboost as xgb
import numpy as np
import requests
import os
from database import (
    save_prediction,
    get_all_predictions,
    update_result,
    calculate_success_rates,
)

router = APIRouter(prefix="/predict", tags=["Predictions"])

# ✅ Load your trained XGBoost model once
MODEL_PATH = "models/nba_xgboost.json"
model = None
if os.path.exists(MODEL_PATH):
    model = xgb.Booster()
    model.load_model(MODEL_PATH)
    print("✅ XGBoost model loaded successfully.")

# ✅ Team logo mappings
TEAM_LOGOS = {
    "Boston Celtics": "bos",
    "Brooklyn Nets": "bkn",
    "New York Knicks": "nyk",
    "Miami Heat": "mia",
    "Chicago Bulls": "chi",
    "Cleveland Cavaliers": "cle",
    "Golden State Warriors": "gsw",
    "Los Angeles Lakers": "lal",
    "Phoenix Suns": "phx",
    "Milwaukee Bucks": "mil",
    "Dallas Mavericks": "dal",
    "Denver Nuggets": "den",
    "Memphis Grizzlies": "mem",
    "Sacramento Kings": "sac",
    "San Antonio Spurs": "sas",
    "Utah Jazz": "uta",
    "Toronto Raptors": "tor",
    "Philadelphia 76ers": "phi",
    "Washington Wizards": "was",
    "Houston Rockets": "hou",
    "Oklahoma City Thunder": "okc",
    "Minnesota Timberwolves": "min",
    "Atlanta Hawks": "atl",
    "Detroit Pistons": "det",
    "Portland Trail Blazers": "por",
    "New Orleans Pelicans": "nop",
    "Orlando Magic": "orl",
    "Indiana Pacers": "ind",
    "Los Angeles Clippers": "lac",
    "Charlotte Hornets": "cha",
}

def get_logo(team):
    key = TEAM_LOGOS.get(team)
    return f"https://a.espncdn.com/i/teamlogos/nba/500/{key}.png" if key else ""

# ✅ Odds API Key
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "e11d4159145383afd3a188f99489969e")

# ✅ Free fallback API for games
def fetch_fallback_games():
    try:
        resp = requests.get("https://www.balldontlie.io/api/v1/games?dates[]=2025-11-05")
        data = resp.json().get("data", [])
        games = []
        for g in data:
            games.append({
                "home_team": g["home_team"]["full_name"],
                "away_team": g["visitor_team"]["full_name"],
                "commence_time": g["date"],
            })
        return games
    except Exception as e:
        print("Fallback API failed:", e)
        return []

# ✅ Main Odds API puller
def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h,spreads,totals&apiKey={ODDS_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                print("⚠️ No games returned from Odds API, using fallback")
                return fetch_fallback_games()
            games = []
            for g in data:
                bookmakers = g.get("bookmakers", [])
                if not bookmakers:
                    continue

                book = bookmakers[0]
                markets = {m["key"]: m for m in book.get("markets", [])}

                games.append({
                    "home_team": g["home_team"],
                    "away_team": g["away_team"],
                    "commence_time": g["commence_time"],
                    "bookmaker": book["title"],
                    "home_odds": next((o["price"] for o in markets.get("h2h", {}).get("outcomes", []) if o["name"] == g["home_team"]), None),
                    "away_odds": next((o["price"] for o in markets.get("h2h", {}).get("outcomes", []) if o["name"] == g["away_team"]), None),
                    "spread": markets.get("spreads", {}).get("outcomes", []),
                    "totals": markets.get("totals", {}).get("outcomes", []),
                })
            return games
        else:
            print(f"⚠️ Odds API failed ({response.status_code}): {response.text}")
            return fetch_fallback_games()
    except Exception as e:
        print("⚠️ Exception fetching odds:", e)
        return fetch_fallback_games()


# ✅ Predict Endpoint
@router.get("/")
def predict_games():
    odds_data = fetch_odds()
    enriched = []

    for g in odds_data:
        home = g["home_team"]
        away = g["away_team"]

        enriched.append({
            "homeTeam": home,
            "awayTeam": away,
            "logos": {"home": get_logo(home), "away": get_logo(away)},
            "bookmaker": g.get("bookmaker"),
            "markets": {
                "moneyline": {"home": g.get("home_odds"), "away": g.get("away_odds")},
                "spread": g.get("spread"),
                "total": g.get("totals")
            },
            "gameTime": g.get("commence_time"),
        })

    return {"timestamp": datetime.now(timezone.utc).isoformat(), "games": enriched}

# ✅ Run Model on specific game
@router.post("/model")
def run_model_prediction(game: dict):
    if not model:
        return {"error": "Model not loaded."}

    home_team = game.get("homeTeam")
    away_team = game.get("awayTeam")

    # Example features for demonstration — replace with real preprocessed inputs later
    features = np.random.rand(1, 10)
    dmatrix = xgb.DMatrix(features)
    preds = model.predict(dmatrix)

    # Example placeholders for bet types
    moneyline_pred = float(preds[0])
    spread_pred = float(preds[0] * 0.8 + 0.1)
    total_pred = float(preds[0] * 1.1 - 0.05)

    # Save to DB
    timestamp = datetime.now(timezone.utc).isoformat()
    save_prediction(timestamp, home_team, away_team, "moneyline", "Home" if moneyline_pred > 0.5 else "Away", round(moneyline_pred * 100, 2))
    save_prediction(timestamp, home_team, away_team, "spread", "Cover" if spread_pred > 0.5 else "No Cover", round(spread_pred * 100, 2))
    save_prediction(timestamp, home_team, away_team, "total", "Over" if total_pred > 0.5 else "Under", round(total_pred * 100, 2))

    return {
        "predictions": {
            "moneyline": {"prediction": "Home" if moneyline_pred > 0.5 else "Away", "confidence": round(moneyline_pred * 100, 2)},
            "spread": {"prediction": "Cover" if spread_pred > 0.5 else "No Cover", "confidence": round(spread_pred * 100, 2)},
            "total": {"prediction": "Over" if total_pred > 0.5 else "Under", "confidence": round(total_pred * 100, 2)},
        }
    }

# ✅ Get Prediction History
@router.get("/history")
def get_prediction_history():
    try:
        return {"history": get_all_predictions()}
    except Exception as e:
        print("⚠️ Error reading history:", e)
        return {"error": str(e)}

# ✅ Update Result (Mark as Success/Fail)
@router.post("/update_result/{prediction_id}")
def mark_result(prediction_id: int, result: str):
    try:
        update_result(prediction_id, result)
        return {"status": "ok", "id": prediction_id, "result": result}
    except Exception as e:
        return {"error": str(e)}

# ✅ Success Rates Summary
@router.get("/success_rates")
def get_success_rates():
    return calculate_success_rates()

# ✅ Background Task - Auto update results
def auto_update_results():
    try:
        print("🔁 Running auto-update for results...")
        # Fetch recent games from balldontlie API
        response = requests.get("https://www.balldontlie.io/api/v1/games?dates[]=2025-11-05")
        data = response.json().get("data", [])

        # Map team -> latest score
        live_scores = {
            (g["home_team"]["full_name"], g["visitor_team"]["full_name"]): {
                "home_score": g["home_team_score"],
                "away_score": g["visitor_team_score"],
                "status": g["status"],
            }
            for g in data
        }

        # Update DB if games finished
        for (home, away), info in live_scores.items():
            if info["status"] == "Final":
                if info["home_score"] > info["away_score"]:
                    update_result_for_game(home, away, "Home")
                else:
                    update_result_for_game(home, away, "Away")

        print("✅ Auto update complete")
    except Exception as e:
        print("⚠️ Auto-update error:", e)

def update_result_for_game(home_team, away_team, winner):
    from database import get_all_predictions
    all_preds = get_all_predictions()
    for p in all_preds:
        if p["home_team"] == home_team and p["away_team"] == away_team:
            if p["prediction"].lower() == winner.lower() or (
                p["prediction"].lower() in ["cover", "over"] and winner.lower() == "home"
            ):
                update_result(p["id"], "success")
            else:
                update_result(p["id"], "fail")

# ✅ Endpoint to manually trigger updates
@router.post("/auto_update")
def manual_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(auto_update_results)
    return {"message": "Background result update started."}
