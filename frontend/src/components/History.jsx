import React, { useEffect, useState } from "react";

const History = () => {
  const [history, setHistory] = useState([]);
  const [rates, setRates] = useState({});

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    fetch(`${API_URL}/predict/history`)
      .then(res => res.json())
      .then(json => setHistory(json.history || []))
      .catch(err => console.error("Error fetching history:", err));

    fetch(`${API_URL}/predict/success_rates`)
      .then(res => res.json())
      .then(json => setRates(json))
      .catch(err => console.error("Error fetching rates:", err));
  }, []);

  const getResultIcon = (result) => {
    if (result === "success") return <span style={{ color: "limegreen" }}>✅</span>;
    if (result === "fail") return <span style={{ color: "red" }}>❌</span>;
    return <span style={{ color: "gray" }}>⏳</span>;
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Poppins, sans-serif", color: "#eee" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>📊 Backtesting & Prediction History</h1>

      <div style={{ marginBottom: "1.5rem", background: "#1e1e2f", padding: "1rem", borderRadius: "10px" }}>
        <h2>Overall Success Rates</h2>
        <p>🏀 Moneyline: <strong>{rates.moneyline || 0}%</strong></p>
        <p>📏 Spread: <strong>{rates.spread || 0}%</strong></p>
        <p>🔢 Total (O/U): <strong>{rates.total || 0}%</strong></p>
      </div>

      <table style={{
        width: "100%",
        borderCollapse: "collapse",
        background: "#1e1e2f",
        color: "white",
        borderRadius: "12px",
        overflow: "hidden"
      }}>
        <thead style={{ background: "#27293d" }}>
          <tr>
            <th>Game</th>
            <th>Bet Type</th>
            <th>Prediction</th>
            <th>Confidence</th>
            <th>Result</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {history.length > 0 ? history.map((p) => (
            <tr key={p.id} style={{ textAlign: "center", borderBottom: "1px solid #333" }}>
              <td>{p.home_team} vs {p.away_team}</td>
              <td>{p.bet_type}</td>
              <td>{p.prediction}</td>
              <td>{p.confidence ? `${p.confidence}%` : "--"}</td>
              <td>{getResultIcon(p.result)}</td>
              <td>{new Date(p.timestamp).toLocaleString()}</td>
            </tr>
          )) : (
            <tr><td colSpan="6" style={{ padding: "1rem" }}>No predictions yet.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default History;
