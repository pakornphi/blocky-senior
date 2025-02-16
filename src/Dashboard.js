import React, { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

function Dashboard() {
  const [urls, setUrls] = useState([]);
  const [csrfResult, setCsrfResult] = useState(null);
  const [brokenAccessControlResult, setBrokenAccessControlResult] = useState(null);

  useEffect(() => {
    const storedUrls = JSON.parse(localStorage.getItem("checkedUrls")) || [];
    setUrls(storedUrls);

    const csrf = JSON.parse(localStorage.getItem("csrfResult"));
    if (csrf) setCsrfResult(csrf);

    const bac = JSON.parse(localStorage.getItem("brokenAccessControlResult"));
    if (bac) setBrokenAccessControlResult(bac);
  }, []);

  const getCsrfPassed = () => {
    if (csrfResult) {
      console.log("CSRF Result: ", csrfResult);
      const validMessages = [
        "CSRF token found",
        "CSRF protection successful: cannot submit without CSRF token",
        "CSRF protection successful: cannot submit with reused CSRF token"
      ];
      const resultMessages = csrfResult.slice(1); 
      const allValid = resultMessages.every(result => validMessages.includes(result));
      console.log("Is CSRF Passed? ", allValid);
      return allValid;
    }
    return false;
  };
  

  const renderPieChart = (label, passed) => {
    const data = {
      labels: [],
      datasets: [{
        data: [passed ? 100 : 0, passed ? 0 : 100],
        backgroundColor: ["#36A2EB", "#FF6384"],
      }],
    };
    return <Pie data={data} />;
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="content">
        <div className="sidebar">
          <h3>URLs</h3>
          <ul>
            {urls.length ? urls.map((url, i) => <li key={i}>{url}</li>) : <p>No URLs checked yet</p>}
          </ul>
        </div>

        <div className="result-columns">
          {["CSRF", "SQL Injection", "XSS", "IDOR", "BAC"].map(test => (
            <div key={test} className={`result-column ${test.toLowerCase()}`}>
              <h2>{test}</h2>
              {renderPieChart(test, test === "CSRF" ? getCsrfPassed() : test === "BAC" ? brokenAccessControlResult?.passed : false)}
              <div className="test-result-box">
                {test === "CSRF" && csrfResult ? <pre>{JSON.stringify(csrfResult, null, 2)}</pre> : 
                 test === "BAC" && brokenAccessControlResult ? <pre>{JSON.stringify(brokenAccessControlResult, null, 2)}</pre> : 
                 <p>No result available</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
