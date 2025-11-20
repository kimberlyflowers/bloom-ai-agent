import { useEffect, useState, useRef } from 'react'

export default function Dashboard() {
  const [sarah, setSarah] = useState(null)
  const [liveScreen, setLiveScreen] = useState(null)
  const [screenConnected, setScreenConnected] = useState(false)
  const [screenActivity, setScreenActivity] = useState([]) // Activity feed for screen
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
  const screenWsRef = useRef(null) // WebSocket for screen activity
  const messagesEndRef = useRef(null)
  const chatMessagesRef = useRef(null)
  const screenActivityRef = useRef(null) // Ref for screen activity container
  const fileInputRef = useRef(null)
  const [uploadingFile, setUploadingFile] = useState(false)

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
  const getWebSocketUrl = () => {
    // Check if we're in production (Vercel)
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      // Production - use Railway
      const envUrl = process.env.NEXT_PUBLIC_RAILWAY_WS_URL
      if (envUrl) {
        return envUrl.replace(/:\d+$/, '').replace(/\/$/, '')
      }
      // Fallback to Railway URL if env var not set
      return 'wss://bloom-ai-agent-production.up.railway.app'
    }
    // Local development
    return 'ws://localhost:8080'
  }

  useEffect(() => {
    setSarah({
      name: "Sarah Rodriguez",
      role: "Growth & Community Lead",
      location: "Phoenix, Arizona",
      specialization: "TikTok growth & UGC creation"
    })

    connectToChat()
    connectToScreen()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (chatWsRef.current) {
        chatWsRef.current.close()
      }
      if (screenWsRef.current) {
        screenWsRef.current.close()
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

  // Auto-scroll screen activity to bottom when new activity arrives
  useEffect(() => {
    if (screenActivityRef.current) {
      screenActivityRef.current.scrollTop = screenActivityRef.current.scrollHeight
    }
  }, [screenActivity])

  function connectToChat() {
    try {
      const baseUrl = getWebSocketUrl()
      // Add /chat path
      const wsUrl = `${baseUrl}/chat`
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
            // Show system message temporarily, but don't save to database or accumulate
            // Only show if it's not already in the last few messages
            const systemMessage = {
              id: Date.now(),
              type: 'system',
              text: data.message,
              timestamp: new Date()
            }
            setMessages(prev => {
              // Don't add if last message was same system message
              const lastMsg = prev[prev.length - 1]
              if (lastMsg && lastMsg.type === 'system' && lastMsg.text === data.message) {
                return prev
              }
              return [...prev, systemMessage]
            })
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

  function connectToScreen() {
    try {
      const baseUrl = getWebSocketUrl()
      // Add /screen path
      const wsUrl = `${baseUrl}/screen`
      console.log('🎥 Connecting to screen:', wsUrl)
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('🎥 Connected to Sarah\'s screen!')
        setScreenConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'screen_connected') {
            console.log('🎥 Screen ready:', data.message)
          } else if (data.type === 'screen_activity') {
            // Add activity to feed (keep last 20 items)
            setScreenActivity(prev => {
              const newActivity = {
                id: Date.now(),
                activity_type: data.activity_type,
                content: data.content,
                timestamp: data.timestamp,
                data: data.data
              }
              const updated = [...prev, newActivity]
              return updated.slice(-20) // Keep last 20 activities
            })
          }
        } catch (error) {
          console.error('Error parsing screen message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ Screen error:', error)
        setScreenConnected(false)
      }

      ws.onclose = () => {
        console.log('🔴 Screen disconnected')
        setScreenConnected(false)
        setTimeout(connectToScreen, 5000) // Reconnect after 5 seconds
      }

      screenWsRef.current = ws
    } catch (error) {
      console.error('Error connecting to screen:', error)
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

  async function handleFileUpload(e) {
    const file = e.target.files?.[0]
    if (!file || !currentConversationIdRef.current) return

    setUploadingFile(true)

    try {
      // Create form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('conversation_id', currentConversationIdRef.current)

      // Upload file
      const response = await fetch(`${getApiUrl()}/api/upload`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      // Show file in chat
      const fileMessage = {
        id: Date.now(),
        type: 'user',
        text: `📎 ${file.name}`,
        file: {
          name: file.name,
          type: file.type,
          url: data.url
        },
        timestamp: new Date()
      }
      setMessages(prev => [...prev, fileMessage])

      // Send to Sarah via WebSocket
      chatWsRef.current.send(JSON.stringify({
        type: 'user_message',
        message: `[File uploaded: ${file.name}]`,
        file: data,
        conversation_id: currentConversationIdRef.current
      }))

      console.log('✅ File uploaded:', data)
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setUploadingFile(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
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
          {(!conversations || conversations.length === 0) ? (
            <div className="no-conversations">
              <p>No conversations yet</p>
              <p className="hint">Click + to start chatting</p>
            </div>
          ) : (
            conversations.map(conv => (
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
            ))
          )}
        </div>
      </div>

      {/* Toggle Button - Outside sidebar so it's always visible */}
      <button
        className="toggle-sidebar-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{ left: sidebarOpen ? '300px' : '0' }}
      >
        {sidebarOpen ? '◀' : '▶'}
      </button>

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

        {/* KPI Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">💚</div>
            <div className="stat-content">
              <div className="stat-label">Health Score</div>
              <div className="stat-value">{chatConnected && screenConnected ? '100%' : chatConnected ? '75%' : '0%'}</div>
              <div className="stat-change">{chatConnected ? '✅ Online' : '🔴 Connecting...'}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💬</div>
            <div className="stat-content">
              <div className="stat-label">Conversations</div>
              <div className="stat-value">{conversations.length}</div>
              <div className="stat-change">Total chats</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📨</div>
            <div className="stat-content">
              <div className="stat-label">Messages</div>
              <div className="stat-value">{messages.filter(m => m.type !== 'system').length}</div>
              <div className="stat-change">This conversation</div>
            </div>
          </div>
        </div>

        {/* Sarah's Live Screen */}
        <div className="card">
          <h2>🎥 Sarah&apos;s Screen</h2>
          <div className="screen-window">
            <div className="screen-status">
              {screenConnected ? (
                <span className="status-indicator connected">🟢 Live</span>
              ) : (
                <span className="status-indicator disconnected">🔴 Connecting...</span>
              )}
            </div>

            {screenActivity.length === 0 ? (
              <div className="screen-placeholder">
                <div className="screen-icon">💤</div>
                <p>Ready and waiting for tasks...</p>
                <p className="screen-hint">Sarah will show her work here in real-time</p>
              </div>
            ) : (
              <div className="screen-activity-feed" ref={screenActivityRef}>
                {screenActivity.map((activity, index) => {
                  // Truncate long content
                  const displayContent = activity.content.length > 80
                    ? activity.content.substring(0, 80) + '...'
                    : activity.content;

                  return (
                    <div key={activity.id || index} className={`activity-item activity-${activity.activity_type}`}>
                      <div className="activity-icon">
                        {activity.activity_type === 'reading' && '📖'}
                        {activity.activity_type === 'thinking' && '🤔'}
                        {activity.activity_type === 'responding' && '💬'}
                        {activity.activity_type === 'file_upload' && '📎'}
                        {activity.activity_type === 'analyzing' && '🔍'}
                        {activity.activity_type === 'analysis_complete' && '✅'}
                        {activity.activity_type === 'waiting' && '⏳'}
                        {activity.activity_type === 'queued' && '📬'}
                        {activity.activity_type === 'status' && '💼'}
                      </div>
                      <div className="activity-content">
                        <div className="activity-text">{displayContent}</div>
                        <div className="activity-time">
                          {new Date(activity.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
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
                    <div className="message-text">
                      {msg.text}
                      {msg.file && msg.file.type && msg.file.type.startsWith('image/') && msg.file.url && (
                        <div className="message-file-preview">
                          <img src={msg.file.url} alt={msg.file.name} />
                        </div>
                      )}
                      {msg.file && msg.file.type && !msg.file.type.startsWith('image/') && msg.file.url && (
                        <div className="message-file-link">
                          <a href={msg.file.url} target="_blank" rel="noopener noreferrer">
                            📄 {msg.file.name}
                          </a>
                        </div>
                      )}
                    </div>
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
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*,video/*,.pdf,.doc,.docx,.txt"
              style={{ display: 'none' }}
            />
            <button
              type="button"
              className="file-upload-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={!chatConnected || uploadingFile}
              title="Upload file (images, videos, docs)"
            >
              {uploadingFile ? '⏳' : '📎'}
            </button>
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
        .no-conversations {
          padding: 3rem 1.5rem;
          text-align: center;
          color: #9ca3af;
        }
        .no-conversations p {
          margin: 0.5rem 0;
        }
        .no-conversations .hint {
          font-size: 0.875rem;
          color: #6b7280;
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
          transition: left 0.3s ease;
          z-index: 50;
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
          background: transparent;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          color: #9ca3af;
          text-align: center;
          max-width: 100%;
        }
        .message-system .message-content {
          background: transparent;
          box-shadow: none;
          padding: 0;
        }
        .message-system .message-text {
          color: #9ca3af;
          font-size: 0.75rem;
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
        .message-file-preview {
          margin-top: 0.5rem;
          border-radius: 8px;
          overflow: hidden;
          max-width: 400px;
        }
        .message-file-preview img {
          width: 100%;
          height: auto;
          display: block;
          border-radius: 8px;
        }
        .message-file-link {
          margin-top: 0.5rem;
        }
        .message-file-link a {
          color: #3b82f6;
          text-decoration: none;
          font-size: 0.875rem;
        }
        .message-file-link a:hover {
          text-decoration: underline;
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
        .file-upload-button {
          padding: 0.75rem;
          background: #f3f4f6;
          color: #6b7280;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1.25rem;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 48px;
        }
        .file-upload-button:hover:not(:disabled) {
          background: #e5e7eb;
          border-color: #a855f7;
        }
        .file-upload-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
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
          background: #0f172a;
          border-radius: 8px;
          padding: 1rem;
          width: 100%;
          aspect-ratio: 16 / 9;
          overflow-y: auto;
          border: 1px solid #1e293b;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .screen-status {
          margin-bottom: 1rem;
          padding: 0.5rem;
          text-align: right;
        }
        .status-indicator {
          font-size: 0.75rem;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.1);
        }
        .status-indicator.connected {
          color: #10b981;
          font-weight: 600;
        }
        .status-indicator.disconnected {
          color: #ef4444;
          font-weight: 600;
        }
        .screen-placeholder {
          color: #ffffff;
          text-align: center;
          padding: 6rem 2rem;
        }
        .screen-placeholder p {
          color: #ffffff;
          font-size: 1.125rem;
          margin-top: 1rem;
          font-weight: 500;
        }
        .screen-placeholder .screen-hint {
          color: #94a3b8;
          font-size: 0.875rem;
          font-weight: 400;
        }
        .screen-icon {
          font-size: 5rem;
          margin-bottom: 1rem;
          opacity: 0.7;
        }
        .screen-activity-feed {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-height: calc(100% - 3rem);
          overflow-y: auto;
          padding-right: 0.5rem;
        }
        .screen-activity-feed::-webkit-scrollbar {
          width: 6px;
        }
        .screen-activity-feed::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .screen-activity-feed::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
        .screen-activity-feed::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        .activity-item {
          display: flex;
          gap: 0.5rem;
          padding: 0.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 6px;
          border-left: 3px solid #3b82f6;
          animation: slideIn 0.3s ease-out;
          flex-shrink: 0;
        }
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .activity-item.activity-reading {
          border-left-color: #3b82f6;
        }
        .activity-item.activity-thinking {
          border-left-color: #8b5cf6;
        }
        .activity-item.activity-responding {
          border-left-color: #10b981;
        }
        .activity-item.activity-file_upload {
          border-left-color: #f59e0b;
        }
        .activity-item.activity-analyzing {
          border-left-color: #06b6d4;
        }
        .activity-item.activity-analysis_complete {
          border-left-color: #10b981;
        }
        .activity-item.activity-waiting {
          border-left-color: #fbbf24;
        }
        .activity-item.activity-queued {
          border-left-color: #ef4444;
        }
        .activity-icon {
          font-size: 1.25rem;
          flex-shrink: 0;
          line-height: 1;
        }
        .activity-content {
          flex: 1;
          min-width: 0;
        }
        .activity-text {
          color: #e2e8f0;
          font-size: 0.8125rem;
          line-height: 1.4;
          word-wrap: break-word;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .activity-time {
          color: #64748b;
          font-size: 0.6875rem;
          margin-top: 0.125rem;
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
