# 🌸 BLOOM AI Agent - Web Dashboard

**Beautiful, modern web dashboard for BLOOM AI Agent**

## ✨ Features

- **Real-Time Updates**: Live data streaming (simulated)
- **KPI Dashboard**: Revenue, costs, ROI, and agent status
- **AI Insights**: Critical and high-priority recommendations
- **Agent Monitoring**: Track all AI agents and their performance
- **Campaign Progress**: Visual campaign tracking with progress bars
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful UI**: Modern gradient design with Tailwind CSS
- **React-Powered**: Interactive single-page application

## 🚀 Quick Start

### Option 1: Open Directly in Browser

Simply open `index.html` in any modern web browser:

```bash
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

### Option 2: Serve with Python

```bash
# Python 3
python -m http.server 8000 --directory .

# Then open http://localhost:8000 in your browser
```

### Option 3: Serve with Node.js

```bash
npx http-server . -p 8000

# Then open http://localhost:8000 in your browser
```

## 📊 Dashboard Sections

### 1. KPIs (Top Row)
- **Total Revenue**: Aggregate revenue from all agents
- **Total Cost**: Total AI/API costs
- **Average ROI**: Overall return on investment
- **Active Agents**: Number of running agents

### 2. Critical Insights
Red-highlighted actionable insights that require immediate attention:
- Scale opportunities (high ROI agents)
- Urgent optimizations needed
- Budget alerts

### 3. AI Agents
Cards showing each agent:
- Agent name and status (running/paused)
- Current ROI
- Revenue and cost breakdown
- Number of actions taken

### 4. Active Campaigns
Campaign cards with:
- Campaign name and phase
- Progress percentage (visual bar)
- Current ROI
- Tasks completed

### 5. High Priority Insights
Orange-highlighted insights:
- Growth predictions
- Optimization recommendations
- Trend analysis

## 🎨 Design Highlights

- **Purple Gradient Header**: Eye-catching brand identity
- **Card Hover Effects**: Smooth animations on interaction
- **Live Update Banner**: Green banner shows real-time updates
- **Color-Coded Status**: Instant visual feedback
- **Responsive Grid**: Adapts to any screen size

## 🔗 Integration with Backend

This UI is designed to integrate with the BLOOM backend systems:

- **Real-Time Dashboard Backend** (`src/realtime_dashboard.py`)
- **AI Insights Engine** (`src/ai_insights.py`)
- **Health Checks** (`src/health_checks.py`)
- **Monitoring & Observability** (`src/monitoring_observability.py`)

### WebSocket Integration (Production)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update dashboard with real data
    updateAgents(data.agents);
    updateCampaigns(data.campaigns);
    updateInsights(data.insights);
};
```

### Server-Sent Events (SSE) Integration

```javascript
const eventSource = new EventSource('/api/events');

eventSource.addEventListener('agent.status.changed', (event) => {
    const data = JSON.parse(event.data);
    updateAgentStatus(data);
});

eventSource.addEventListener('insight.generated', (event) => {
    const insight = JSON.parse(event.data);
    addInsight(insight);
});
```

## 🛠️ Customization

### Change Theme Colors

Edit the Tailwind classes in `index.html`:

```javascript
// Current purple theme
className="gradient-bg" // Purple gradient

// Change to blue
className="bg-gradient-to-r from-blue-500 to-cyan-600"
```

### Add More Agents/Campaigns

Modify the mock data:

```javascript
const mockAgents = [
    // Add your agents here
    { id: '004', name: 'Your Agent', status: 'running', roi: 2.5, ... }
];
```

### Connect to Real Backend

Replace mock data with API calls:

```javascript
useEffect(() => {
    fetch('/api/agents')
        .then(res => res.json())
        .then(data => setAgents(data));
}, []);
```

## 📱 Mobile Support

The dashboard is fully responsive and works perfectly on:
- ✅ Desktop (1920x1080 and above)
- ✅ Laptop (1366x768)
- ✅ Tablet (iPad, Android tablets)
- ✅ Mobile (iPhone, Android phones)

## 🚀 Production Deployment

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=.
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Deploy to GitHub Pages

```bash
# Push to GitHub
git add .
git commit -m "Add web dashboard"
git push origin main

# Enable GitHub Pages in repository settings
# Point to /web directory
```

## 🎯 Future Enhancements

- [ ] Add dark mode toggle
- [ ] Implement user authentication
- [ ] Add export to PDF/CSV
- [ ] Interactive charts (Chart.js/D3.js)
- [ ] Drag-and-drop dashboard customization
- [ ] Multi-user support
- [ ] Advanced filtering and search
- [ ] Agent creation wizard
- [ ] Campaign builder interface

## 📄 License

Part of BLOOM AI Agent - Enterprise Marketing Intelligence Platform

Built with ❤️ by Claude
