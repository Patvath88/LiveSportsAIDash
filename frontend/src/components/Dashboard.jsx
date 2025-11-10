// frontend/src/components/Dashboard.jsx

import React, { useEffect, useState } from "react";
import "./Dashboard.css";

const Dashboard = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedGame, setSelectedGame] = useState(null);
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/predict/")
      .then((res) => res.json())
      .then((data) => {
        setGames(data.games || []);
        setLoading(false);
      })
      .catch(() => {
        setError("Unable to load live NBA data.");
        setLoading(false);
      });
  }, []);

  const runPrediction = (game) => {
    setSelectedGame(game);
    setPrediction({ loading: true });

    fetch("http://127.0.0.1:8000/predict/model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(game),
    })
      .then((res) => res.json())
      .then((result) => {
        setPrediction({
          loading: false,
          data: result.predictions || {},
          edge: result.edge || 0,
        });
      })
      .catch(() => setPrediction({ error: "Error running prediction" }));
  };

  const closeModal = () => {
    setSelectedGame(null);
    setPrediction(null);
  };

  const safeOdds = (oddsObj, key) => {
    if (!oddsObj) return "--";
    return oddsObj[key] ?? "--";
  };

  if (loading) return <div className="loading">Loading live NBA data...</div>;
  if (error) return <div className="error">{error}</div>;

  const handleLogoError = (e) => {
    e.target.src =
      "https://upload.wikimedia.org/wikipedia/en/0/03/NBA_logo.svg";
  };

  return (
    <div className="dashboard">
      <h1 className="title">🏀 NBA AI Prediction & Betting Dashboard</h1>

      <div className="games-grid">
        {games.map((g, i) => (
          <div key={i} className="game-card">
            <div className="teams">
              <div className="team">
                <img
                  src={g.logos.home}
                  alt={g.homeTeam}
                  onError={handleLogoError}
                />
                <span>{g.homeTeam}</span>
              </div>
              <div className="vs">vs</div>
              <div className="team">
                <img
                  src={g.logos.away}
                  alt={g.awayTeam}
                  onError={handleLogoError}
                />
                <span>{g.awayTeam}</span>
              </div>
            </div>

            <div className="details">
              <div className="odds">
                <div>
                  <strong>Spread:</strong> {safeOdds(g.odds, "spread")}
                </div>
                <div>
                  <strong>Moneyline:</strong> {safeOdds(g.odds, "moneyline")}
                </div>
                <div>
                  <strong>Total:</strong> {safeOdds(g.odds, "total")}
                </div>
              </div>

              <div className="meta">
                <div>
                  <strong>Game Time:</strong> {g.gameTime || "TBD"}
                </div>
                <div>
                  <strong>Score:</strong>{" "}
                  {g.scores?.home || 0} - {g.scores?.away || 0}
                </div>
              </div>

              <button
                onClick={() => runPrediction(g)}
                className="predict-button"
              >
                Predict
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedGame && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            {prediction?.loading ? (
              <div className="modal-loading">Running AI Prediction...</div>
            ) : prediction?.error ? (
              <div className="modal-error">{prediction.error}</div>
            ) : (
              <>
                <h2>AI Prediction Result</h2>
                <div className="modal-content">
                  <p>
                    <strong>Matchup:</strong> {selectedGame.homeTeam} vs{" "}
                    {selectedGame.awayTeam}
                  </p>
                  <div className="prediction-table">
                    <div><strong>Bet Type</strong></div>
                    <div><strong>Prediction</strong></div>
                    <div><strong>Confidence</strong></div>

                    <div>Moneyline</div>
                    <div>{prediction.data.moneyline?.pick || "--"}</div>
                    <div>
                      {Math.round(
                        (prediction.data.moneyline?.confidence || 0) * 100
                      )}
                      %
                    </div>

                    <div>Spread</div>
                    <div>{prediction.data.spread?.pick || "--"}</div>
                    <div>
                      {Math.round(
                        (prediction.data.spread?.confidence || 0) * 100
                      )}
                      %
                    </div>

                    <div>Total (O/U)</div>
                    <div>{prediction.data.total?.pick || "--"}</div>
                    <div>
                      {Math.round(
                        (prediction.data.total?.confidence || 0) * 100
                      )}
                      %
                    </div>
                  </div>

                  <p>
                    <strong>Value Edge vs Book:</strong>{" "}
                    <span
                      className={
                        parseFloat(prediction.edge) > 0
                          ? "edge-positive"
                          : "edge-negative"
                      }
                    >
                      {prediction.edge || 0}%
                    </span>
                  </p>
                </div>
                <div className="modal-actions">
                  <button className="save-btn">Save Prediction</button>
                  <button onClick={closeModal} className="close-btn">
                    Close
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
