import { useEffect, useState, useRef } from 'react'

export default function CommandCenter() {
  // Active tasks (dynamically spawned agents currently working)
  const [activeTasks, setActiveTasks] = useState([])

  // Approval queue (content waiting for review)
  const [approvalQueue, setApprovalQueue] = useState([])

  // WebSocket connection state
  const [connected, setConnected] = useState(false)
  const [liveUpdate, setLiveUpdate] = useState(null)
  const wsRef = useRef(null)

  // Connect to command center WebSocket
  useEffect(() => {
    connectToCommandCenter()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  function connectToCommandCenter() {
    try {
      // Use Railway WebSocket URL with /command path
      const railwayUrl = process.env.NEXT_PUBLIC_RAILWAY_WS_URL
      const wsUrl = railwayUrl ? `${railwayUrl}/command` : 'ws://localhost:8080/command'

      console.log('🎛️  Connecting to command center:', wsUrl)
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('✅ Connected to command center')
        setConnected(true)
        setLiveUpdate('Connected to command center')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('📥 Command center message:', data.type)

          if (data.type === 'initial_data') {
            // Initial data: active tasks and pending approvals
            setActiveTasks(data.active_tasks || [])
            setApprovalQueue(data.pending_approvals || [])
            setLiveUpdate('Received initial data')
          } else if (data.type === 'task_started') {
            // New agent spawned - add to active tasks
            setActiveTasks(prev => [...prev, data.task])
            setLiveUpdate(`Started: ${data.task.agent_type}`)
          } else if (data.type === 'task_progress') {
            // Agent progress update
            setActiveTasks(prev => prev.map(t =>
              t.task_id === data.task_id ? { ...t, progress: data.progress } : t
            ))
            setLiveUpdate(`Progress: ${data.progress}`)
          } else if (data.type === 'task_completed') {
            // Agent finished - remove from active tasks
            setActiveTasks(prev => prev.filter(t => t.task_id !== data.task_id))
            setLiveUpdate(`Completed: ${data.task_id}`)
          } else if (data.type === 'new_content') {
            // Content created - add to approval queue
            setApprovalQueue(prev => [...prev, data.content])
            setLiveUpdate(`New content: ${data.content.title}`)
          } else if (data.type === 'approval_action') {
            // Content approved/rejected - remove from queue
            setApprovalQueue(prev => prev.filter(c => c.content_id !== data.content_id))
            setLiveUpdate(`${data.action}: ${data.content_id}`)
          }
        } catch (e) {
          console.error('Error parsing message:', e)
        }
      }

      ws.onclose = () => {
        console.log('🔌 Disconnected from command center')
        setConnected(false)
        setLiveUpdate('Disconnected')

        // Auto-reconnect after 5 seconds
        setTimeout(connectToCommandCenter, 5000)
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        setLiveUpdate('Connection error')
      }
    } catch (error) {
      console.error('Error connecting to command center:', error)
    }
  }

  const sendCommand = (command) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command))
      console.log('📤 Sent command:', command.type)
    }
  }

  const approveContent = (contentId) => {
    sendCommand({
      type: 'approve_content',
      content_id: contentId,
      feedback: 'Approved!'
    })
  }

  const rejectContent = (contentId, feedback) => {
    sendCommand({
      type: 'reject_content',
      content_id: contentId,
      feedback: feedback || 'Please revise'
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center text-white font-bold text-xl">
                🌸
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">BLOOM Command Center</h1>
                <p className="text-sm text-gray-600">Sarah's Multi-Agent Orchestration Dashboard</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-sm font-medium">{connected ? 'Connected' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-purple-100">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl">
                🎯
              </div>
              <div>
                <p className="text-sm text-gray-600">Active Tasks</p>
                <p className="text-3xl font-bold text-gray-900">{activeTasks.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-yellow-100">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center text-2xl">
                ⏳
              </div>
              <div>
                <p className="text-sm text-gray-600">Pending Approval</p>
                <p className="text-3xl font-bold text-gray-900">{approvalQueue.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-green-100">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
                ✨
              </div>
              <div>
                <p className="text-sm text-gray-600">System Status</p>
                <p className="text-xl font-bold text-green-600">Operational</p>
              </div>
            </div>
          </div>
        </div>

        {/* Live Update Banner */}
        {liveUpdate && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <div className="flex items-center gap-2 text-blue-700">
              <span className="text-lg">📡</span>
              <span className="font-medium">Latest Update:</span>
              <span>{liveUpdate}</span>
              <span className="ml-auto text-sm text-blue-600">
                {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}

        {/* Active Tasks Section */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Active Tasks</h2>
          <p className="text-sm text-gray-600 mb-4">
            Specialized agents that Sarah has spawned to handle complex requests
          </p>

          {activeTasks.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-200">
              <div className="text-6xl mb-4">😴</div>
              <p className="text-lg font-medium text-gray-600">No active tasks</p>
              <p className="text-sm text-gray-500 mt-2">
                Agents are spawned dynamically when Sarah receives complex requests
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {activeTasks.map((task, i) => (
                <div key={i} className="bg-white rounded-xl shadow-sm p-6 border border-purple-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">
                          {task.agent_type === 'VideoCreationAgent' ? '🎬' :
                           task.agent_type === 'ResearchAgent' ? '🔍' :
                           task.agent_type === 'ContentPostingAgent' ? '📱' : '🤖'}
                        </span>
                        <h3 className="text-lg font-bold text-gray-900">{task.agent_type}</h3>
                        <span className="ml-auto px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                          Active
                        </span>
                      </div>
                      <p className="text-gray-700 mb-3">{task.description}</p>
                      {task.progress && (
                        <div className="bg-gray-100 rounded-lg p-3">
                          <p className="text-sm text-gray-600">{task.progress}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Approval Queue Section */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">✅ Approval Queue</h2>
          <p className="text-sm text-gray-600 mb-4">
            Content created by agents waiting for your review before publishing
          </p>

          {approvalQueue.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-200">
              <div className="text-6xl mb-4">✨</div>
              <p className="text-lg font-medium text-gray-600">No pending approvals</p>
              <p className="text-sm text-gray-500 mt-2">
                Content will appear here when agents create videos or other content
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {approvalQueue.map((item, i) => (
                <div key={i} className="bg-white rounded-xl shadow-md border border-yellow-200 overflow-hidden">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                        <p className="text-sm text-gray-600 mb-3">{item.description}</p>

                        {/* Metadata */}
                        <div className="flex flex-wrap gap-2 mb-4">
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {item.content_type}
                          </span>
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {item.platform}
                          </span>
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {item.duration || 'N/A'}
                          </span>
                        </div>

                        {/* Script/Caption */}
                        {item.script && (
                          <div className="bg-gray-50 rounded-lg p-3 mb-4">
                            <p className="text-xs font-medium text-gray-600 mb-1">SCRIPT:</p>
                            <p className="text-sm text-gray-700">{item.script}</p>
                          </div>
                        )}

                        {item.caption && (
                          <div className="bg-blue-50 rounded-lg p-3 mb-4">
                            <p className="text-xs font-medium text-blue-600 mb-1">CAPTION:</p>
                            <p className="text-sm text-gray-700">{item.caption}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                      <button
                        onClick={() => approveContent(item.content_id)}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition"
                      >
                        ✅ Approve
                      </button>
                      <button
                        onClick={() => {
                          const feedback = prompt('Feedback for agent:')
                          if (feedback) rejectContent(item.content_id, feedback)
                        }}
                        className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-4 rounded-lg transition"
                      >
                        ❌ Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
