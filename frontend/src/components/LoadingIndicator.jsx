import React from 'react';

/**
 * LoadingIndicator - Visual feedback while awaiting backend response
 * 
 * Displays animated dots to indicate loading state
 */
function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="loading-bubble">
        <span className="dot"></span>
        <span className="dot"></span>
        <span className="dot"></span>
      </div>
    </div>
  );
}

export default LoadingIndicator;
