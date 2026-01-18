import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import AnomalyDashboard from './AnomalyDashboard';

/**
 * MessageBubble - Single message unit
 * 
 * Props:
 * - role: 'user' | 'assistant'
 * - content: String message content
 * - chartData: Optional chart data for anomaly visualizations
 * 
 * User messages: rendered as plain text
 * Assistant messages: rendered via MarkdownRenderer + optional chart
 */
function MessageBubble({ role, content, chartData, media }) {
  const isUser = role === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-role">
        {isUser ? 'You' : 'Assistant'}
      </div>
      <div className="message-content">
        {isUser ? (
          <p>{content}</p>
        ) : (
          <>
            <MarkdownRenderer content={content} />
            {chartData && (
              <div style={{ 
                marginTop: '20px',
                maxWidth: '100%',
                overflowX: 'auto',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '10px'
              }}>
                <AnomalyDashboard data={chartData} media={media} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
