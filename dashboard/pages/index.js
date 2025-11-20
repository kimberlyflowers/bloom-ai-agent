import { useEffect, useState, useRef } from 'react'

export default function Dashboard() {
  const [sarah, setSarah] = useState(null)
  const [liveScreen, setLiveScreen] = useState(null)
  const [screenConnected, setScreenConnected] = useState(false)
  const wsRef = useRef(null)

  // Chat state
  const [messages, setMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatConnected, setChatConnected] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const chatWsRef = useRef(null)
  const messagesEndRef = useRef(null)

  // WebSocket URLs - use environment variable or localhost for development
  const getWebSocketUrl = (port) => {
    // Check if we have a Railway URL from environment variable
    const railwayUrl = process.env.NEXT_PUBLIC_RAILWAY_WS_URL
    if (railwayUrl) {
      // Railway uses a single PORT for all connections
      // Just use the Railway URL directly (wss:// for secure connection)
      // Railway will route based on its internal PORT environment variable
      return railwayUrl
    }
    // Fallback to localhost for development (with specific ports)
    return `ws://localhost:${port}`
  }

  useEffect(() => {
    setSarah({
      name: "Sarah Rodriguez",
      role: "Growth & Community Lead",
      location: "Phoenix, Arizona",
      specialization: "TikTok growth & UGC creation"
    })

    // Connect to live screen stream
    // NOTE: Temporarily disabled - Railway only supports one PORT
    // We'll refactor to use single server with multiple endpoints later
    // connectToLiveScreen()

    // Connect to chat server
    connectToChat()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (chatWsRef.current) {
        chatWsRef.current.close()
      }
    }
  }, [])

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function connectToLiveScreen() {
    try {
      // Connect to Railway WebSocket server
      const wsUrl = getWebSocketUrl(8765)
      console.log('🎥 Connecting to screen stream:', wsUrl)
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('📺 Connected to Sarah\'s screen!')
        setScreenConnected(true)
      }

      ws.onmessage = (event) => {
        const data = event.data

        if (data.startsWith('FRAME:')) {
          // Received a new frame
          const frameData = data.substring(6)
          setLiveScreen(`data:image/jpeg;base64,${frameData}`)
        } else if (data.startsWith('CONNECTED:')) {
          console.log('✅ Screen stream ready')
        }
      }

      ws.onerror = (error) => {
        console.error('❌ Screen stream error:', error)
        setScreenConnected(false)
      }

      ws.onclose = () => {
        console.log('🔴 Screen stream disconnected')
        setScreenConnected(false)

        // Auto-reconnect after 5 seconds
        setTimeout(connectToLiveScreen, 5000)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Error connecting to screen stream:', error)
    }
  }

  function connectToChat() {
    try {
      // Connect to chat WebSocket endpoint
      const baseUrl = getWebSocketUrl(8766)
      // Add /chat path for FastAPI WebSocket endpoint
      const wsUrl = baseUrl.includes('localhost') ? baseUrl : `${baseUrl}/chat`
      console.log('💬 Connecting to chat:', wsUrl)
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('💬 Connected to Sarah\'s chat!')
        setChatConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'system') {
            // System message (welcome, etc.)
            setMessages(prev => [...prev, {
              id: Date.now(),
              type: 'system',
              text: data.message,
              timestamp: new Date()
            }])
          } else if (data.type === 'sarah_message') {
            // Message from Sarah
            setMessages(prev => [...prev, {
              id: Date.now(),
              type: 'sarah',
              text: data.message,
              timestamp: new Date()
            }])
            setIsSending(false)
          }
        } catch (error) {
          console.error('Error parsing chat message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ Chat error:', error)
        setChatConnected(false)
      }

      ws.onclose = () => {
        console.log('🔴 Chat disconnected')
        setChatConnected(false)

        // Auto-reconnect after 5 seconds
        setTimeout(connectToChat, 5000)
      }

      chatWsRef.current = ws
    } catch (error) {
      console.error('Error connecting to chat:', error)
    }
  }

  function sendMessage(e) {
    e.preventDefault()

    if (!chatInput.trim() || !chatConnected || isSending) {
      return
    }

    // Add user message to UI
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: chatInput,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    // Send to Sarah via WebSocket
    chatWsRef.current.send(JSON.stringify({
      type: 'user_message',
      message: chatInput
    }))

    // Clear input and set sending state
    setChatInput('')
    setIsSending(true)
  }

  if (!sarah) {
    return <div className="loading">Loading Sarah...</div>
  }

  return (
    <div className="container">
      {/* Header */}
      <div className="header">
        <div className="avatar">SR</div>
        <div className="header-info">
          <h1>{sarah.name}</h1>
          <p>🌸 AI Agent Employee • {sarah.role} at BLOOM</p>
        </div>
        <div className="status-badge">
          <div className="status-dot"></div>
          Online
        </div>
      </div>

      {/* Metrics */}
      <div className="metrics">
        <div className="metric-card pink">
          <div className="metric-icon">💝</div>
          <div className="metric-label">Trust Score</div>
          <div className="metric-value">50.0</div>
        </div>
        <div className="metric-card blue">
          <div className="metric-icon">🤝</div>
          <div className="metric-label">Relationships</div>
          <div className="metric-value">0</div>
        </div>
        <div className="metric-card purple">
          <div className="metric-icon">✨</div>
          <div className="metric-label">Value Provided</div>
          <div className="metric-value">0</div>
        </div>
        <div className="metric-card green">
          <div className="metric-icon">💰</div>
          <div className="metric-label">Revenue</div>
          <div className="metric-value">$0</div>
        </div>
      </div>

      {/* LIVE SCREEN VIEW - THE COOLEST FEATURE! */}
      <div className="live-screen-card">
        <div className="live-screen-header">
          <h2>🎥 Sarah's Live Screen</h2>
          <div className={screenConnected ? "stream-status connected" : "stream-status disconnected"}>
            <div className="stream-dot"></div>
            {screenConnected ? 'LIVE' : 'Offline'}
          </div>
        </div>

        <div className="live-screen-viewer">
          {liveScreen ? (
            <img
              src={liveScreen}
              alt="Sarah's live screen"
              className="live-screen-image"
            />
          ) : (
            <div className="no-stream">
              <div className="no-stream-icon">📺</div>
              <p>{screenConnected ? 'Waiting for Sarah to start working...' : 'Connecting to live stream...'}</p>
            </div>
          )}
        </div>

        <div className="live-screen-info">
          <p>💡 Watch Sarah work in real-time! You'll see her create emails, browse TikTok, and more!</p>
        </div>
      </div>

      {/* CHAT WITH SARAH - TALK TO HER IN REAL-TIME! */}
      <div className="chat-card">
        <div className="chat-header">
          <h2>💬 Chat with Sarah</h2>
          <div className={chatConnected ? "stream-status connected" : "stream-status disconnected"}>
            <div className="stream-dot"></div>
            {chatConnected ? 'Online' : 'Offline'}
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="no-messages">
              <div className="no-messages-icon">💬</div>
              <p>Start a conversation with Sarah!</p>
              <p className="no-messages-hint">Ask her about her work, TikTok strategies, or anything else 🌸</p>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`message message-${msg.type}`}>
                {msg.type === 'sarah' && <div className="message-avatar">SR</div>}
                <div className="message-content">
                  {msg.type === 'sarah' && <div className="message-sender">Sarah Rodriguez</div>}
                  {msg.type === 'user' && <div className="message-sender">You</div>}
                  <div className="message-text">{msg.text}</div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {msg.type === 'user' && <div className="message-avatar-user">You</div>}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder={chatConnected ? "Type a message to Sarah..." : "Connecting to chat..."}
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            disabled={!chatConnected || isSending}
          />
          <button
            type="submit"
            className="chat-send-button"
            disabled={!chatConnected || !chatInput.trim() || isSending}
          >
            {isSending ? '...' : '➤'}
          </button>
        </form>
      </div>

      {/* Activity */}
      <div className="card">
        <h2>Current Activity</h2>
        <div className="activity">
          <div className="activity-icon">😴</div>
          <div>
            <p className="activity-text">Sleeping for 1 hour...</p>
            <p className="activity-time">
              Next check-in at {new Date(Date.now() + 3600000).toLocaleTimeString()}
            </p>
          </div>
        </div>
      </div>

      {/* Identity */}
      <div className="card">
        <h2>Sarah&apos;s Identity</h2>
        <div className="details">
          <div className="detail">
            <strong>Location:</strong> {sarah.location}
          </div>
          <div className="detail">
            <strong>Email:</strong> sarah@trybloom.ai
          </div>
          <div className="detail">
            <strong>Specialization:</strong> {sarah.specialization}
          </div>
          <div className="detail">
            <strong>Role:</strong> {sarah.role}
          </div>
        </div>
      </div>

      {/* Daily Routine */}
      <div className="card">
        <h2>Daily Routine</h2>
        <div className="routine">
          <div className="routine-item complete">
            <span>📧</span> Check email
            <span className="routine-check">✓</span>
          </div>
          <div className="routine-item complete">
            <span>💝</span> Manage relationships
            <span className="routine-check">✓</span>
          </div>
          <div className="routine-item complete">
            <span>✅</span> Update metrics
            <span className="routine-check">✓</span>
          </div>
          <div className="routine-item active">
            <span>😴</span> Sleep 1 hour
            <span className="routine-check">⋯</span>
          </div>
        </div>
      </div>

      <div className="footer">
        <p>🌸 Powered by BLOOM AI Agents • Running 24/7 on Railway</p>
      </div>

      <style jsx>{`
        .container {
          min-height: 100vh;
          background: linear-gradient(to bottom right, #fdf2f8, #fae8ff);
          padding: 2rem;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .loading {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          color: #6b7280;
        }
        .header {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .avatar {
          width: 64px;
          height: 64px;
          background: linear-gradient(135deg, #ec4899, #a855f7);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 1.5rem;
          font-weight: bold;
        }
        .header-info h1 {
          font-size: 2rem;
          font-weight: bold;
          color: #111827;
          margin: 0;
        }
        .header-info p {
          color: #6b7280;
          margin: 0.25rem 0 0 0;
        }
        .status-badge {
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #dcfce7;
          color: #166534;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-weight: 500;
        }
        .status-dot {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .metric-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
        }
        .metric-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          margin-bottom: 0.75rem;
        }
        .pink .metric-icon { background: linear-gradient(135deg, #ec4899, #db2777); }
        .blue .metric-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .purple .metric-icon { background: linear-gradient(135deg, #a855f7, #9333ea); }
        .green .metric-icon { background: linear-gradient(135deg, #10b981, #059669); }
        .metric-label {
          color: #6b7280;
          font-size: 0.875rem;
          margin-bottom: 0.25rem;
        }
        .metric-value {
          font-size: 2rem;
          font-weight: bold;
          color: #111827;
        }
        .live-screen-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 6px 12px rgba(236, 72, 153, 0.15);
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          border: 2px solid #fce7f3;
        }
        .live-screen-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        .live-screen-header h2 {
          font-size: 1.5rem;
          font-weight: bold;
          color: #111827;
          margin: 0;
        }
        .stream-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-weight: 600;
          font-size: 0.875rem;
        }
        .stream-status.connected {
          background: #dcfce7;
          color: #166534;
        }
        .stream-status.disconnected {
          background: #fee2e2;
          color: #991b1b;
        }
        .stream-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: currentColor;
        }
        .stream-status.connected .stream-dot {
          animation: pulse 2s infinite;
        }
        .live-screen-viewer {
          background: #111827;
          border-radius: 8px;
          aspect-ratio: 16 / 9;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          position: relative;
          margin-bottom: 1rem;
        }
        .live-screen-image {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }
        .no-stream {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          color: #9ca3af;
        }
        .no-stream-icon {
          font-size: 4rem;
          opacity: 0.5;
        }
        .no-stream p {
          margin: 0;
          font-size: 1rem;
        }
        .live-screen-info {
          background: #fef3c7;
          border-left: 4px solid #f59e0b;
          padding: 0.75rem;
          border-radius: 4px;
        }
        .live-screen-info p {
          margin: 0;
          color: #92400e;
          font-size: 0.875rem;
        }
        .card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }
        .card h2 {
          font-size: 1.5rem;
          font-weight: bold;
          color: #111827;
          margin: 0 0 1rem 0;
        }
        .activity {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .activity-icon {
          font-size: 3rem;
        }
        .activity-text {
          font-size: 1.125rem;
          font-weight: 500;
          color: #111827;
          margin: 0;
        }
        .activity-time {
          color: #6b7280;
          font-size: 0.875rem;
          margin: 0.25rem 0 0 0;
        }
        .details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }
        .detail {
          border-left: 3px solid #ec4899;
          padding-left: 0.75rem;
          color: #111827;
        }
        .detail strong {
          color: #6b7280;
          font-size: 0.875rem;
          display: block;
          margin-bottom: 0.25rem;
        }
        .routine {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .routine-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: #f9fafb;
          border-radius: 8px;
        }
        .routine-item span:first-child {
          font-size: 1.5rem;
        }
        .routine-check {
          margin-left: auto;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 500;
        }
        .routine-item.complete .routine-check {
          background: #dcfce7;
          color: #166534;
        }
        .routine-item.active .routine-check {
          background: #fef3c7;
          color: #92400e;
        }
        .footer {
          text-align: center;
          color: #6b7280;
          margin-top: 2rem;
        }
        .chat-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 6px 12px rgba(168, 85, 247, 0.15);
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          border: 2px solid #f3e8ff;
          display: flex;
          flex-direction: column;
          height: 600px;
        }
        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          flex-shrink: 0;
        }
        .chat-header h2 {
          font-size: 1.5rem;
          font-weight: bold;
          color: #111827;
          margin: 0;
        }
        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 8px;
          margin-bottom: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .no-messages {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 0.5rem;
          color: #9ca3af;
        }
        .no-messages-icon {
          font-size: 4rem;
          opacity: 0.5;
        }
        .no-messages p {
          margin: 0;
          font-size: 1rem;
        }
        .no-messages-hint {
          font-size: 0.875rem !important;
          color: #6b7280;
        }
        .message {
          display: flex;
          gap: 0.75rem;
          align-items: flex-start;
        }
        .message-sarah {
          align-self: flex-start;
        }
        .message-user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }
        .message-system {
          align-self: center;
          background: #fef3c7;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-size: 0.875rem;
          color: #92400e;
        }
        .message-avatar {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #ec4899, #a855f7);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 0.875rem;
          flex-shrink: 0;
        }
        .message-avatar-user {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 0.875rem;
          flex-shrink: 0;
        }
        .message-content {
          max-width: 70%;
          background: white;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .message-user .message-content {
          background: #eff6ff;
        }
        .message-sender {
          font-weight: 600;
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.25rem;
        }
        .message-text {
          color: #111827;
          font-size: 0.9375rem;
          line-height: 1.5;
          word-wrap: break-word;
          white-space: pre-wrap;
        }
        .message-time {
          font-size: 0.75rem;
          color: #9ca3af;
          margin-top: 0.25rem;
        }
        .chat-input-container {
          display: flex;
          gap: 0.75rem;
          flex-shrink: 0;
        }
        .chat-input {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 0.9375rem;
          transition: border-color 0.2s;
        }
        .chat-input:focus {
          outline: none;
          border-color: #a855f7;
        }
        .chat-input:disabled {
          background: #f3f4f6;
          cursor: not-allowed;
        }
        .chat-send-button {
          padding: 0.75rem 1.5rem;
          background: linear-gradient(135deg, #a855f7, #9333ea);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1.25rem;
          cursor: pointer;
          transition: opacity 0.2s;
        }
        .chat-send-button:hover:not(:disabled) {
          opacity: 0.9;
        }
        .chat-send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  )
}
