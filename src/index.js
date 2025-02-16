import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';  // Import Router, Routes, and Route
import './index.css';
import App from './App';
import Dashboard from './Dashboard';  // Import Dashboard component
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>  {/* Wrap the app with Router to enable routing */}
      <Routes>  {/* Define the routes */}
        <Route path="/" element={<App />} />  {/* Route for the main app */}
        <Route path="/dashboard" element={<Dashboard />} />  {/* Route for the dashboard */}
      </Routes>
    </Router>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
