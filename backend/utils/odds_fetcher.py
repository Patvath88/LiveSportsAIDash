# backend/utils/odds_fetcher.py
import requests

API_KEY = "e11d4159145383afd3a188f99489969e"

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=american"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        games = []
        for g in data:
            bookmaker = g["bookmakers"][0] if g["bookmakers"] else {}
            markets = {m["key"]: m for m in bookmaker.get("markets", [])}
            home_team = g["home_team"]
            away_team = g["away_team"]
            commence = g["commence_time"]

            moneyline = markets.get("h2h", {}).get("outcomes", [])
            spread = markets.get("spreads", {}).get("outcomes", [])
            totals = markets.get("totals", {}).get("outcomes", [])

            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": commence,
                "moneyline": next((o["price"] for o in moneyline if o["name"] == home_team), None),
                "spread": next((o["point"] for o in spread if o["name"] == home_team), None),
                "totals": next((o["point"] for o in totals if o["name"] == "Over"), None),
                "scores": g.get("scores", {}),
            })
        return games
    except Exception as e:
        print("❌ Odds fetch failed:", e)
        return []
