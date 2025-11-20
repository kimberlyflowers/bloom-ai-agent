import { useEffect, useState, useRef } from 'react'

export default function Dashboard() {
  const [sarah, setSarah] = useState(null)
  const [liveScreen, setLiveScreen] = useState(null)
  const [screenConnected, setScreenConnected] = useState(false)
  const wsRef = useRef(null)

  // Conversation state
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const currentConversationIdRef = useRef(null) // Ref to avoid stale closure in WebSocket
  const [messages, setMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatConnected, setChatConnected] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const chatWsRef = useRef(null)
  const messagesEndRef = useRef(null)
  const chatMessagesRef = useRef(null)

  // Keep ref in sync with state
  useEffect(() => {
    currentConversationIdRef.current = currentConversationId
    console.log('📡 Current conversation ID updated to:', currentConversationId)
  }, [currentConversationId])

  // API base URL
  const getApiUrl = () => {
    const railwayUrl = process.env.NEXT_PUBLIC_RAILWAY_WS_URL
    if (railwayUrl) {
      return railwayUrl.replace('wss://', 'https://').replace('ws://', 'http://')
    }
    return 'http://localhost:8080'
  }

  // Load conversations from API on mount
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const apiUrl = getApiUrl()
      console.log('📡 Loading conversations from:', `${apiUrl}/api/conversations`)
      const response = await fetch(`${apiUrl}/api/conversations`)
      console.log('📡 Response status:', response.status)
      const data = await response.json()
      console.log('📡 Response data:', data)

      if (data && data.conversations && data.conversations.length > 0) {
        console.log('📡 Found', data.conversations.length, 'conversations')
        setConversations(data.conversations)

        // Load the most recent conversation
        const mostRecent = data.conversations[0]
        setCurrentConversationId(mostRecent.id)
        await loadConversationMessages(mostRecent.id)
      } else {
        // Create first conversation
        console.log('📡 No conversations found, creating new one...')
        await createNewConversation()
      }
    } catch (error) {
      console.error('Error loading conversations:', error)
      // Fallback to creating new conversation
      await createNewConversation()
    }
  }

  const refreshConversationsList = async () => {
    // Refresh conversation list without changing current conversation
    try {
      const response = await fetch(`${getApiUrl()}/api/conversations`)
      const data = await response.json()
      if (data && data.conversations) {
        setConversations(data.conversations)
      }
    } catch (error) {
      console.error('Error refreshing conversations:', error)
    }
  }

  const loadConversationMessages = async (conversationId) => {
    try {
      const response = await fetch(`${getApiUrl()}/api/conversations/${conversationId}/messages`)
      const data = await response.json()

      // Convert API messages to frontend format
      const formattedMessages = data.messages.map(msg => ({
        id: msg.id,
        type: msg.type,
        text: msg.text,
        timestamp: new Date(msg.timestamp)
      }))

      setMessages(formattedMessages)
    } catch (error) {
      console.error('Error loading messages:', error)
      setMessages([])
    }
  }

  const createNewConversation = async () => {
    try {
      const newId = Date.now().toString()
      console.log('📡 Creating conversation with ID:', newId)

      const response = await fetch(`${getApiUrl()}/api/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: newId })
      })

      console.log('📡 Create response status:', response.status)
      const newConv = await response.json()
      console.log('📡 Created conversation:', newConv)

      setConversations(prev => [newConv, ...prev])
      setCurrentConversationId(newConv.id)
      setMessages([])
      console.log('📡 Conversation ID set to:', newConv.id)
    } catch (error) {
      console.error('Error creating conversation:', error)
    }
  }

  const switchConversation = async (convId) => {
    setCurrentConversationId(convId)
    await loadConversationMessages(convId)
  }

  const deleteConversation = async (convId, e) => {
    e.stopPropagation()

    try {
      await fetch(`${getApiUrl()}/api/conversations/${convId}`, {
        method: 'DELETE'
      })

      const updated = conversations.filter(c => c.id !== convId)
      setConversations(updated)

      // If deleting current conversation, switch to another
      if (convId === currentConversationId) {
        if (updated.length > 0) {
          await switchConversation(updated[0].id)
        } else {
          await createNewConversation()
        }
      }
    } catch (error) {
      console.error('Error deleting conversation:', error)
    }
  }

  const getConversationTitle = (conv) => {
    // Title is managed by the API based on first user message
    return conv.title || 'New conversation'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`

    return date.toLocaleDateString()
  }

  // WebSocket URLs - use environment variable or localhost for development
  const getWebSocketUrl = (port) => {
    const railwayUrl = process.env.NEXT_PUBLIC_RAILWAY_WS_URL
    if (railwayUrl) {
      return railwayUrl
    }
    return `ws://localhost:${port}`
  }

  useEffect(() => {
    setSarah({
      name: "Sarah Rodriguez",
      role: "Growth & Community Lead",
      location: "Phoenix, Arizona",
      specialization: "TikTok growth & UGC creation"
    })

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

  // Smart auto-scroll: only scroll to bottom if user is already near the bottom
  useEffect(() => {
    if (!chatMessagesRef.current) return

    const container = chatMessagesRef.current
    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100

    if (isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  function connectToChat() {
    try {
      const baseUrl = getWebSocketUrl(8766)
      // Add /chat path if not already present
      let wsUrl = baseUrl
      if (!baseUrl.includes('localhost') && !baseUrl.endsWith('/chat')) {
        wsUrl = `${baseUrl}/chat`
      }
      console.log('💬 Connecting to chat:', wsUrl)
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('💬 Connected to Sarah\'s chat!')
        setChatConnected(true)
      }

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'system') {
            // Don't display or save "Connected to Sarah" messages - they're just connection noise
            // User can see connection status in the header already
            console.log('🔔 System message (not displayed):', data.message)
          } else if (data.type === 'sarah_message') {
            const sarahMessage = {
              id: Date.now(),
              type: 'sarah',
              text: data.message,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, sarahMessage])
            setIsSending(false)

            // Save Sarah's response to database
            if (currentConversationIdRef.current) {
              try {
                await fetch(`${getApiUrl()}/api/conversations/${currentConversationIdRef.current}/messages`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ type: 'sarah', text: data.message })
                })
              } catch (error) {
                console.error('Error saving Sarah message to database:', error)
              }
            }
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
        setTimeout(connectToChat, 5000)
      }

      chatWsRef.current = ws
    } catch (error) {
      console.error('Error connecting to chat:', error)
    }
  }

  async function sendMessage(e) {
    e.preventDefault()

    if (!chatInput.trim() || !chatConnected || isSending || !currentConversationIdRef.current) {
      return
    }

    const messageText = chatInput
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: messageText,
      timestamp: new Date()
    }

    // Add to UI immediately
    setMessages(prev => [...prev, userMessage])
    setChatInput('')
    setIsSending(true)

    // Send via WebSocket for real-time response (with conversation_id for server-side persistence)
    chatWsRef.current.send(JSON.stringify({
      type: 'user_message',
      message: messageText,
      conversation_id: currentConversationIdRef.current
    }))

    // Save to database via API
    try {
      await fetch(`${getApiUrl()}/api/conversations/${currentConversationIdRef.current}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'user', text: messageText })
      })

      // Refresh conversations list to get updated title (if this was the first message)
      await refreshConversationsList()
    } catch (error) {
      console.error('Error saving user message to database:', error)
    }
  }

  if (!sarah) {
    return <div className="loading">Loading Sarah...</div>
  }

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>💬 Conversations</h2>
          <button onClick={() => createNewConversation()} className="new-conversation-btn" title="New conversation">
            +
          </button>
        </div>

        <div className="conversations-list">
          {(conversations || []).map(conv => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
              onClick={() => switchConversation(conv.id)}
            >
              <div className="conversation-content">
                <div className="conversation-title">{getConversationTitle(conv)}</div>
                <div className="conversation-date">{formatDate(conv.updatedAt)}</div>
              </div>
              <button
                className="delete-conversation-btn"
                onClick={(e) => deleteConversation(conv.id, e)}
                title="Delete conversation"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <button
          className="toggle-sidebar-btn"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? '◀' : '▶'}
        </button>
      </div>

      {/* Main Content */}
      <div className="main-content">
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

        {/* Chat Card */}
        <div className="chat-card">
          <div className="chat-header">
            <h2>💬 Chat with Sarah</h2>
            <div className={chatConnected ? "stream-status connected" : "stream-status disconnected"}>
              <div className="stream-dot"></div>
              {chatConnected ? 'Online' : 'Offline'}
            </div>
          </div>

          <div className="chat-messages" ref={chatMessagesRef}>
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

        {/* Sarah's Live Screen */}
        <div className="card">
          <h2>🎥 Sarah&apos;s Screen</h2>
          <div className="screen-window">
            <div className="screen-placeholder">
              <div className="screen-icon">🖥️</div>
              <p>Screen sharing coming soon!</p>
              <p className="screen-hint">You&apos;ll be able to see what Sarah is working on in real-time</p>
            </div>
          </div>
        </div>

        {/* KPI Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <div className="stat-label">Revenue Generated</div>
              <div className="stat-value">$0</div>
              <div className="stat-change">Coming soon</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-label">ROI</div>
              <div className="stat-value">-</div>
              <div className="stat-change">Tracking starts when Sarah works</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-label">Tasks Completed</div>
              <div className="stat-value">0</div>
              <div className="stat-change">This week</div>
            </div>
          </div>
        </div>

        {/* Activity */}
        <div className="card">
          <h2>Current Activity</h2>
          <div className="activity">
            <div className="activity-icon">💬</div>
            <div>
              <p className="activity-text">Chatting with you!</p>
              <p className="activity-time">
                {messages.length} messages in this conversation
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

        <div className="footer">
          <p>🌸 Powered by BLOOM AI Agents • Running 24/7 on Railway</p>
        </div>
      </div>

      <style jsx>{`
        .dashboard-container {
          display: flex;
          min-height: 100vh;
          background: linear-gradient(to bottom right, #fdf2f8, #fae8ff);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Sidebar */
        .sidebar {
          width: 300px;
          background: white;
          border-right: 1px solid #e5e7eb;
          display: flex;
          flex-direction: column;
          transition: transform 0.3s ease;
        }
        .sidebar.closed {
          transform: translateX(-100%);
          position: absolute;
        }
        .sidebar-header {
          padding: 1.5rem;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .sidebar-header h2 {
          font-size: 1.25rem;
          font-weight: bold;
          color: #111827;
          margin: 0;
        }
        .new-conversation-btn {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          border: none;
          background: linear-gradient(135deg, #a855f7, #9333ea);
          color: white;
          font-size: 1.5rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: opacity 0.2s;
        }
        .new-conversation-btn:hover {
          opacity: 0.9;
        }
        .conversations-list {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }
        .conversation-item {
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: background 0.2s;
        }
        .conversation-item:hover {
          background: #f3f4f6;
        }
        .conversation-item.active {
          background: #ede9fe;
          border-left: 3px solid #a855f7;
        }
        .conversation-content {
          flex: 1;
          min-width: 0;
        }
        .conversation-title {
          font-size: 0.875rem;
          font-weight: 500;
          color: #111827;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .conversation-date {
          font-size: 0.75rem;
          color: #6b7280;
          margin-top: 0.25rem;
        }
        .delete-conversation-btn {
          width: 24px;
          height: 24px;
          border-radius: 4px;
          border: none;
          background: transparent;
          color: #9ca3af;
          font-size: 1.5rem;
          cursor: pointer;
          display: none;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        .conversation-item:hover .delete-conversation-btn {
          display: flex;
        }
        .delete-conversation-btn:hover {
          background: #fee2e2;
          color: #dc2626;
        }
        .toggle-sidebar-btn {
          position: fixed;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 32px;
          height: 64px;
          border: none;
          background: white;
          border-radius: 0 8px 8px 0;
          box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
          cursor: pointer;
          font-size: 1rem;
          color: #6b7280;
          transition: all 0.2s;
          z-index: 10;
        }
        .sidebar.open .toggle-sidebar-btn {
          left: 300px;
        }
        .toggle-sidebar-btn:hover {
          background: #f3f4f6;
        }

        /* Main Content */
        .main-content {
          flex: 1;
          padding: 2rem;
          overflow-y: auto;
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
          user-select: text;
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
          user-select: text;
          cursor: text;
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
        .screen-window {
          background: #f9fafb;
          border-radius: 8px;
          padding: 3rem;
          text-align: center;
          border: 2px dashed #e5e7eb;
        }
        .screen-placeholder {
          color: #6b7280;
        }
        .screen-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
          opacity: 0.5;
        }
        .screen-hint {
          font-size: 0.875rem;
          color: #9ca3af;
          margin-top: 0.5rem;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        .stat-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .stat-icon {
          font-size: 2.5rem;
        }
        .stat-content {
          flex: 1;
        }
        .stat-label {
          font-size: 0.875rem;
          color: #6b7280;
          font-weight: 500;
          margin-bottom: 0.25rem;
        }
        .stat-value {
          font-size: 1.875rem;
          font-weight: bold;
          color: #111827;
          margin-bottom: 0.25rem;
        }
        .stat-change {
          font-size: 0.75rem;
          color: #9ca3af;
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
        .footer {
          text-align: center;
          color: #6b7280;
          margin-top: 2rem;
        }

        @media (max-width: 768px) {
          .sidebar {
            position: absolute;
            z-index: 20;
            height: 100vh;
          }
          .main-content {
            padding: 1rem;
          }
        }
      `}</style>
    </div>
  )
}
