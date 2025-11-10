import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function AccuracyChart({ data }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Model Accuracy Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(tick) => {
              // If timestamp is ISO (e.g. "2025-11-05T19:20:30")
              if (tick.includes("T")) {
                const time = tick.split("T")[1];
                return time; // show time (HH:MM:SS)
              }
              return tick; // fallback
            }}
            interval="preserveStartEnd"
          />
          <YAxis domain={[0, 1]} />
          <Tooltip
            formatter={(value) => [`${(value * 100).toFixed(1)}%`, "Accuracy"]}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
