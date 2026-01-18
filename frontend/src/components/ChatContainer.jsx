import React, { useRef, useEffect } from 'react';
import MessageList from './MessageList';
import LoadingIndicator from './LoadingIndicator';

/**
 * ChatContainer - Layout wrapper with scroll behavior
 * 
 * Props:
 * - messages: Array of message objects
 * - isLoading: Boolean for showing loading indicator
 */
function ChatContainer({ messages, isLoading, media }) {
  const containerRef = useRef(null);

  // Auto-scroll to bottom when messages change or loading state changes
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="chat-container" ref={containerRef}>
      {messages.length === 0 && !isLoading && (
        <div className="empty-state">
          <p>Ask me anything about click data.</p>
          <p className="hint">Examples: "How many clicks yesterday?", "Top 10 media sources in October"</p>
        </div>
      )}
      
      <MessageList messages={messages} media={media} />
      
      {isLoading && <LoadingIndicator />}
    </div>
  );
}

export default ChatContainer;
