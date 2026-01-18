import React from 'react';

/**
 * Sidebar - Quick actions and system status
 * 
 * Props:
 * - onQuickQuestion: Function to send predefined question
 */
function Sidebar({ onQuickQuestion }) {
  const quickQuestions = [
    { id: 1, label: 'Top 10 Media Sources', query: 'Show me the top 10 media sources' },
    { id: 2, label: 'Anomalies Last 24h', query: 'Show me anomalies in the last 24 hours' },
    { id: 3, label: 'Campaign Performance', query: 'How are my campaigns performing?' },
    { id: 4, label: 'Click Trends', query: 'Show me click trends for this week' },
    { id: 5, label: 'Suspicious Activity', query: 'Are there any suspicious activities?' },
  ];

  return (
    <div className="sidebar">
      {/* System Status */}
      <div className="system-status">
        <div className="status-indicator">
          <span className="pulse-dot"></span>
        </div>
        <div className="status-text">Connected</div>
      </div>

      {/* Quick Questions */}
      <div className="quick-questions">
        <h3 className="sidebar-heading">Quick Questions</h3>
        <div className="question-list">
          {quickQuestions.map((q) => (
            <button
              key={q.id}
              className="question-btn"
              onClick={() => onQuickQuestion(q.query)}
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
