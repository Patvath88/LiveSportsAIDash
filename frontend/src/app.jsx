import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import History from "./components/History";

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-black text-white font-sans">
        <nav className="bg-gray-900 p-4 flex justify-center gap-8 border-b border-cyan-500 shadow-lg relative">
          {[
            { name: "🏀 Dashboard", path: "/" },
            { name: "📊 Backtesting", path: "/history" },
          ].map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `relative text-lg font-semibold tracking-wide ${
                  isActive ? "text-cyan-400" : "text-gray-300 hover:text-cyan-300"
                } transition duration-300`
              }
            >
              {({ isActive }) => (
                <>
                  {link.name}
                  {isActive && (
                    <span className="absolute -bottom-1 left-0 right-0 h-[2px] bg-cyan-400 rounded-full animate-pulse"></span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
