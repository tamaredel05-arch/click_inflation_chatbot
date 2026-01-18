import React, { useState, useCallback } from 'react';
import ChatContainer from './components/ChatContainer';
import ChatInput from './components/ChatInput';
import AnomalyDashboard from './components/AnomalyDashboard';
import Sidebar from './components/Sidebar';
import mockData from './mock_data.json';

/**
 * Generate a UUID v4 for session identification
 */
function generateSessionId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get or create session ID from sessionStorage
 */
function getSessionId() {
  let sessionId = sessionStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    sessionStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}

/**
 * App - Main component
 * 
 * State:
 * - messages: Array of { role: 'user' | 'assistant', content: string }
 * - sessionId: String identifier for this conversation
 * - isLoading: Boolean for loading state
 * - error: String for network/HTTP errors only
 */
function App() {
  console.log('App is rendering!');
  const [messages, setMessages] = useState([]);
  const [sessionId] = useState(getSessionId);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);

  /**
   * Send message to backend POST /chat
   * Appends user message immediately, then appends assistant response
   */
  const sendMessage = useCallback(async (userInput) => {
    if (!userInput.trim() || isLoading) return;

    // Clear any previous error
    setError(null);

    // Append user message immediately
    const userMessage = { role: 'user', content: userInput };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userInput,
        }),
      });

      if (!response.ok) {
        if (response.status >= 500) {
          throw new Error('Server error, please try again');
        }
        throw new Error('Unable to send message');
      }

      const data = await response.json();

      // Extract text from ADK response format
      // Expected: { content: { parts: [{ text: "..." }] } }
      let assistantContent = '';
      if (data?.content?.parts?.[0]?.text) {
        assistantContent = data.content.parts[0].text;
      } else if (typeof data === 'string') {
        assistantContent = data;
      } else if (data?.text) {
        assistantContent = data.text;
      } else if (data?.message) {
        assistantContent = data.message;
      } else {
        assistantContent = JSON.stringify(data);
      }

      // Append assistant message with optional chart data
      const assistantMessage = { 
        role: 'assistant', 
        content: assistantContent,
        chartData: data?.has_chart ? data.chart_data : null
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      // Handle network/HTTP errors only
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Unable to reach server');
      } else {
        setError(err.message || 'Request failed');
      }
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, isLoading]);

  /**
   * Start a new conversation - clears messages and generates new session
   */
  const startNewConversation = useCallback(() => {
    const newSessionId = generateSessionId();
    sessionStorage.setItem('chat_session_id', newSessionId);
    setMessages([]);
    setError(null);
    window.location.reload(); // Reload to reset sessionId state
  }, []);


  console.log('From app -> messages ' , messages);

  const useRole = messages.findLast(user => user.role === 'user');
  const media = useRole && useRole.content && useRole.content.indexOf('פרטנר') > -1 ? 'partner' : 'media';
  return (
    <div className="app">
      <Sidebar onQuickQuestion={sendMessage} />
      
      <div className="main-content">
        <header className="app-header">
          <h1>Click Inflation Chat</h1>
          <div>
            <button 
              className="new-chat-btn" 
              onClick={() => setShowDashboard(!showDashboard)}
              title="Toggle dashboard test"
              style={{ marginRight: '10px' }}
            >
              {showDashboard ? 'Show Chat' : 'Test Dashboard'}
            </button>
            <button 
              className="new-chat-btn" 
              onClick={startNewConversation}
              title="Start new conversation"
            >
              New Chat
            </button>
          </div>
        </header>

        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}

        {showDashboard ? (
          <div style={{ padding: '20px' }}>
            <AnomalyDashboard data={mockData} media={media} change={messages.length}/>
          </div>
        ) : (
          <>
            <ChatContainer messages={messages} media={media} isLoading={isLoading} />
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
