import React from 'react';
import './ReportDisplay.css'; 

function ReportDisplay({ report, isLoading }) {
  if (isLoading) {
    return <div className="report-display-placeholder">Generating report... This may take a moment.</div>;
  }
  if (!report) {
    return <div className="report-display-placeholder">Diagnostic report will appear here after analysis.</div>;
  }

  return (
    <div className="report-display">
      <h3>Diagnostic Report</h3>
      <pre className="report-content">{report}</pre>
    </div>
  );
}

export default ReportDisplay;