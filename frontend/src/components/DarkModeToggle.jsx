import React from 'react';
import './DarkModeToggle.css'; 

function DarkModeToggle({ isDarkMode, toggleDarkMode }) {
  return (
    <button
      onClick={toggleDarkMode}
      className="dark-mode-toggle"
      aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDarkMode ? '☀️' : '🌙'} {}
    </button>
  );
}

export default DarkModeToggle;