# backend/utils/data_fetcher.py

from datetime import datetime
from nba_api.live.nba.endpoints import scoreboard
import requests
import logging
import concurrent.futures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_nba_api_data():
    """Primary data source — NBA.com via nba_api."""
    sb = scoreboard.ScoreBoard()
    data = sb.get_dict()
    games = data.get("scoreboard", {}).get("games", [])
    formatted_games = []

    for g in games:
        home_team = g["homeTeam"]
        away_team = g["awayTeam"]

        formatted_games.append({
            "gameId": g["gameId"],
            "gameStatusText": g.get("gameStatusText"),
            "gameStatus": g.get("gameStatus"),
            "startTime": g.get("gameTimeUTC"),
            "homeTeam": home_team.get("teamTricode"),
            "awayTeam": away_team.get("teamTricode"),
            "homeScore": home_team.get("score"),
            "awayScore": away_team.get("score")
        })

    return formatted_games


def fetch_fallback_data():
    """
    Secondary data source — public JSON mirror (SportsData.io-style).
    Uses ESPN-like open data (no API key needed).
    """
    try:
        resp = requests.get(
            "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json",
            timeout=5
        )
        data = resp.json()
        games = data.get("leagueSchedule", {}).get("gameDates", [])
        formatted = []

        for date_data in games:
            for g in date_data.get("games", []):
                formatted.append({
                    "gameId": g.get("gameId"),
                    "startTime": g.get("gameDateTimeUTC"),
                    "homeTeam": g["homeTeam"]["teamTricode"],
                    "awayTeam": g["awayTeam"]["teamTricode"],
                    "gameStatusText": g.get("gameStatusText", "Scheduled"),
                    "homeScore": g["homeTeam"].get("score"),
                    "awayScore": g["awayTeam"].get("score")
                })
        logger.info(f"✅ Fallback API returned {len(formatted)} games")
        return formatted
    except Exception as e:
        logger.error(f"Fallback API failed: {e}")
        return []


def get_games_data():
    """
    Try NBA.com first. If fails or empty, fall back to open schedule feed.
    Returns only real, live NBA data — never test data.
    """
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_nba_api_data)
            games = future.result(timeout=5)
    except Exception as e:
        logger.error(f"NBA.com fetch failed: {e}")
        games = []

    # If NBA.com returns no live games, try ESPN mirror feed
    if not games:
        logger.warning("NBA API empty, trying fallback feed...")
        games = fetch_fallback_data()

    # Final check
    if not games:
        logger.error("All real NBA sources failed.")
    else:
        logger.info(f"Fetched {len(games)} real NBA games successfully.")

    return games
