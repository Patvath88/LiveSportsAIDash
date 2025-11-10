import sqlite3
from datetime import datetime

DB_PATH = "nba_ai.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            home_team TEXT,
            away_team TEXT,
            home_prob REAL,
            away_prob REAL,
            prediction TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(timestamp, home_team, away_team, home_prob, away_prob, prediction="N/A", confidence=0.0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (timestamp, home_team, away_team, home_prob, away_prob, prediction, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, home_team, away_team, home_prob, away_prob, prediction, confidence))
    conn.commit()
    conn.close()

def get_all_predictions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "home_team": row[2],
            "away_team": row[3],
            "home_prob": row[4],
            "away_prob": row[5],
            "prediction": row[6],
            "confidence": row[7]
        } for row in rows
    ]

# Initialize tables when backend starts
create_tables()
