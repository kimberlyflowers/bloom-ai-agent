import { useEffect, useState, useRef } from 'react'

export default function Dashboard() {
  const [sarah, setSarah] = useState(null)
  const [liveScreen, setLiveScreen] = useState(null)
  const [screenConnected, setScreenConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    setSarah({
      name: "Sarah Rodriguez",
      role: "Growth & Community Lead",
      location: "Phoenix, Arizona",
      specialization: "TikTok growth & UGC creation"
    })

    // Connect to live screen stream
    connectToLiveScreen()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  function connectToLiveScreen() {
    try {
      // Connect to Railway WebSocket server
      // In production, replace with actual Railway URL
      const ws = new WebSocket('ws://localhost:8765')

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
      `}</style>
    </div>
  )
}
