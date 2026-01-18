import React, { useState } from 'react';

/**
 * ChatInput - Text input with submit button
 * 
 * Props:
 * - onSend: Function to call with user input
 * - disabled: Boolean to disable input during loading
 */
function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift for multiline)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chat-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? 'Waiting for response...' : 'Type your question...'}
        disabled={disabled}
        autoFocus
      />
      <button 
        type="submit" 
        className="send-button" 
        disabled={disabled || !input.trim()}
      >
        {disabled ? '...' : 'Send'}
      </button>
    </form>
  );
}

export default ChatInput;
