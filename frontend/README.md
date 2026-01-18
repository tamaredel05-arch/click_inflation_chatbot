# Click Inflation Chat - React Frontend

A thin React client for the Click Inflation analytical backend.

## Architecture

This frontend is intentionally minimal:
- **No analytical logic** — all handled by backend
- **No clarification tracking** — backend manages retry state
- **No interpretation of user intent** — backend decides everything
- **Pure display layer** — renders backend Markdown responses exactly as received

## Setup

```bash
cd frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The app runs at `http://localhost:3000` and proxies `/chat` requests to `http://localhost:8000`.

Make sure the backend is running on port 8000.

## Build for Production

```bash
npm run build
```

Output is in the `dist/` folder.

## Project Structure

```
frontend/
├── src/
│   ├── index.jsx           # Entry point
│   ├── App.jsx             # Main component (state: messages, sessionId, isLoading, error)
│   ├── styles.css          # All styles
│   └── components/
│       ├── ChatContainer.jsx    # Layout with scroll behavior
│       ├── ChatInput.jsx        # Text input + submit
│       ├── LoadingIndicator.jsx # Animated dots during loading
│       ├── MarkdownRenderer.jsx # Markdown/tables/SQL rendering
│       ├── MessageBubble.jsx    # Single message (user vs assistant)
│       └── MessageList.jsx      # Renders all messages
├── index.html
├── package.json
└── vite.config.js
```

## State Management

React state is limited to:

| State | Purpose |
|-------|---------|
| `messages[]` | Array of `{ role, content }` to display |
| `sessionId` | UUID stored in sessionStorage |
| `isLoading` | Disable input during requests |
| `error` | Network/HTTP errors only |

The backend handles:
- Clarification tracking and retry limits
- Follow-up question context
- Slot resolution (date, metric, dimension)
- All analytical logic

## Backend Communication

- **Endpoint:** `POST /chat`
- **Request:** `{ session_id: string, message: string }`
- **Response:** ADK event with `content.parts[0].text` containing Markdown

## Proxy Configuration

In `vite.config.js`, the dev server proxies `/chat` to the backend:

```javascript
proxy: {
  '/chat': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

Adjust the `target` if your backend runs on a different port.
