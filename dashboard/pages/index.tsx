import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [sarah, setSarah] = useState<any>(null)
  const [isOnline, setIsOnline] = useState(false)

  useEffect(() => {
    // For now, we'll just show static data
    // Later we'll connect to Railway API
    setSarah({
      name: "Sarah Rodriguez",
      role: "Growth & Community Lead",
      location: "Phoenix, Arizona",
      specialization: "TikTok growth & UGC creation",
      email: "sarah@trybloom.ai"
    })
    setIsOnline(true)
  }, [])

  if (!sarah) {
    return (
      <div style={styles.loading}>
        <h1>Loading Sarah...</h1>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.avatar}>
            SR
          </div>
          <div>
            <h1 style={styles.name}>{sarah.name}</h1>
            <p style={styles.subtitle}>
              🌸 AI Agent Employee • {sarah.role} at BLOOM
            </p>
          </div>
          <div style={styles.statusBadge}>
            <div style={{
              ...styles.statusDot,
              backgroundColor: isOnline ? '#10b981' : '#ef4444',
              animation: isOnline ? 'pulse 2s infinite' : 'none'
            }} />
            {isOnline ? 'Online' : 'Offline'}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={styles.metricsGrid}>
        <MetricCard
          label="Trust Score"
          value="50.0"
          icon="💝"
          color="#ec4899"
        />
        <MetricCard
          label="Relationships"
          value="0"
          icon="🤝"
          color="#3b82f6"
        />
        <MetricCard
          label="Value Provided"
          value="0"
          icon="✨"
          color="#a855f7"
        />
        <MetricCard
          label="Revenue"
          value="$0"
          icon="💰"
          color="#10b981"
        />
      </div>

      {/* Current Activity */}
      <div style={styles.activityCard}>
        <h2 style={styles.activityTitle}>Current Activity</h2>
        <div style={styles.activityContent}>
          <div style={styles.activityIcon}>😴</div>
          <div>
            <p style={styles.activityText}>
              Sleeping for 1 hour...
            </p>
            <p style={styles.activityTime}>
              Next check-in at {new Date(Date.now() + 3600000).toLocaleTimeString()}
            </p>
          </div>
        </div>
      </div>

      {/* Identity Details */}
      <div style={styles.detailsCard}>
        <h2 style={styles.detailsTitle}>Sarah's Identity</h2>
        <div style={styles.detailsGrid}>
          <DetailItem label="Location" value={sarah.location} />
          <DetailItem label="Email" value={sarah.email} />
          <DetailItem label="Specialization" value={sarah.specialization} />
          <DetailItem label="Role" value={sarah.role} />
        </div>
      </div>

      {/* Daily Routine */}
      <div style={styles.routineCard}>
        <h2 style={styles.routineTitle}>Daily Routine</h2>
        <div style={styles.routineList}>
          <RoutineItem icon="📧" text="Check email" status="complete" />
          <RoutineItem icon="💝" text="Manage relationships" status="complete" />
          <RoutineItem icon="✅" text="Update metrics" status="complete" />
          <RoutineItem icon="😴" text="Sleep 1 hour" status="in-progress" />
        </div>
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <p>🌸 Powered by BLOOM AI Agents • Running 24/7 on Railway</p>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  )
}

function MetricCard({ label, value, icon, color }: any) {
  return (
    <div style={styles.metricCard}>
      <div style={{
        ...styles.metricIcon,
        background: `linear-gradient(135deg, ${color}, ${adjustColor(color, -20)})`
      }}>
        {icon}
      </div>
      <p style={styles.metricLabel}>{label}</p>
      <p style={styles.metricValue}>{value}</p>
    </div>
  )
}

function DetailItem({ label, value }: any) {
  return (
    <div style={styles.detailItem}>
      <p style={styles.detailLabel}>{label}</p>
      <p style={styles.detailValue}>{value}</p>
    </div>
  )
}

function RoutineItem({ icon, text, status }: any) {
  return (
    <div style={styles.routineItem}>
      <span style={styles.routineIcon}>{icon}</span>
      <span style={styles.routineText}>{text}</span>
      <span style={{
        ...styles.routineStatus,
        backgroundColor: status === 'complete' ? '#dcfce7' : '#fef3c7',
        color: status === 'complete' ? '#166534' : '#92400e'
      }}>
        {status === 'complete' ? '✓' : '⋯'}
      </span>
    </div>
  )
}

function adjustColor(color: string, amount: number) {
  return color
}

const styles: any = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(to bottom right, #fdf2f8, #fae8ff)',
    padding: '2rem',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  loading: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.5rem',
    color: '#6b7280'
  },
  header: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    marginBottom: '1.5rem'
  },
  headerContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    flexWrap: 'wrap'
  },
  avatar: {
    width: '64px',
    height: '64px',
    background: 'linear-gradient(135deg, #ec4899, #a855f7)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '1.5rem',
    fontWeight: 'bold'
  },
  name: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#111827',
    margin: 0
  },
  subtitle: {
    color: '#6b7280',
    margin: '0.25rem 0 0 0'
  },
  statusBadge: {
    marginLeft: 'auto',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    backgroundColor: '#dcfce7',
    color: '#166534',
    padding: '0.5rem 1rem',
    borderRadius: '9999px',
    fontWeight: '500'
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1.5rem',
    marginBottom: '1.5rem'
  },
  metricCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem'
  },
  metricIcon: {
    width: '48px',
    height: '48px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.5rem',
    marginBottom: '0.75rem'
  },
  metricLabel: {
    color: '#6b7280',
    fontSize: '0.875rem',
    margin: '0 0 0.25rem 0'
  },
  metricValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#111827',
    margin: 0
  },
  activityCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    marginBottom: '1.5rem'
  },
  activityTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#111827',
    margin: '0 0 1rem 0'
  },
  activityContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem'
  },
  activityIcon: {
    fontSize: '3rem'
  },
  activityText: {
    fontSize: '1.125rem',
    fontWeight: '500',
    color: '#111827',
    margin: 0
  },
  activityTime: {
    color: '#6b7280',
    fontSize: '0.875rem',
    margin: '0.25rem 0 0 0'
  },
  detailsCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    marginBottom: '1.5rem'
  },
  detailsTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#111827',
    margin: '0 0 1rem 0'
  },
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem'
  },
  detailItem: {
    borderLeft: '3px solid #ec4899',
    paddingLeft: '0.75rem'
  },
  detailLabel: {
    color: '#6b7280',
    fontSize: '0.875rem',
    margin: 0,
    fontWeight: '500'
  },
  detailValue: {
    color: '#111827',
    fontSize: '1rem',
    margin: '0.25rem 0 0 0'
  },
  routineCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '1.5rem',
    marginBottom: '1.5rem'
  },
  routineTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#111827',
    margin: '0 0 1rem 0'
  },
  routineList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  routineItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem',
    backgroundColor: '#f9fafb',
    borderRadius: '8px'
  },
  routineIcon: {
    fontSize: '1.5rem'
  },
  routineText: {
    flex: 1,
    color: '#111827',
    fontWeight: '500'
  },
  routineStatus: {
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    fontSize: '0.875rem',
    fontWeight: '500'
  },
  footer: {
    textAlign: 'center',
    color: '#6b7280',
    marginTop: '2rem'
  }
}
