import React from 'react';
import MessageBubble from './MessageBubble';

/**
 * MessageList - Renders array of messages
 * 
 * Props:
 * - messages: Array of { role: 'user' | 'assistant', content: string, chartData?: object }
 */
function MessageList({ messages, media }) {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <MessageBubble 
          media={media}
          key={index} 
          role={message.role} 
          content={message.content}
          chartData={message.chartData}
        />
      ))}
    </div>
  );
}

export default MessageList;
