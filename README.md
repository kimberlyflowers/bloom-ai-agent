# BLOOM AI Growth Agent with Cellular Reproduction

An autonomous AI agent system that grows BLOOM's user base through intelligent Reddit and Twitter marketing. Agents earn commission on conversions, learn from results, and "reproduce" when successful by creating specialized child agents.

## 🌟 Key Features

### 1. Commission-Based Economics
- Agents earn 10% commission on BLOOM user conversions
- Commission funds their own operations (API costs, promotions)
- Self-sustaining growth model

### 2. Adaptive Learning System
- Tracks ROI for every marketing action
- Strategies with high ROI get more budget allocation
- Strategies with low ROI get disabled
- Agent continuously optimizes itself

### 3. Operating Modes
Agents adapt their behavior based on balance:

- **SURVIVAL ($0-$50)**: Conservative, proven tactics only
- **GROWTH ($50-$500)**: Balanced testing + proven strategies
- **SCALE ($500+)**: Aggressive, maximize high performers

### 4. Cellular Reproduction
When agents hit performance benchmarks, they "reproduce":
- Creates specialized child agent
- Parent transfers starting funds to child
- Child inherits parent's ROI knowledge
- Both continue operating independently

### 5. Agent Specializations
- **GENERALIST**: Does everything (founding agents)
- **REDDIT_SPECIALIST**: Reddit-only marketing
- **TWITTER_SPECIALIST**: Twitter-only marketing
- **CONTENT_CREATOR**: Creates posts/threads only
- **COMMUNITY_ENGAGER**: Comments/replies only
- **PAID_ADVERTISER**: Paid promotions (10x budget)
- **ENTERPRISE_HUNTER**: High-value targets (2x commission)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Reddit API credentials
- Twitter API credentials
- Anthropic API key (Claude)

### Installation

```bash
# Clone repository
git clone https://github.com/kimberlyflowers/bloom-ai-agent.git
cd bloom-ai-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your credentials:

```bash
# Anthropic API
ANTHROPIC_API_KEY=your_key_here

# Reddit API
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here

# Twitter API
TWITTER_BEARER_TOKEN=your_token_here
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_SECRET=your_secret_here

# Agent Config
INITIAL_BALANCE=50.0
RUN_MODE=once
```

### Run Demo

```bash
python demo.py
```

The interactive demo showcases all system features:
- Basic agent operation
- Learning system
- Operating modes
- Cellular reproduction
- Full colony simulation

### Run Single Agent

```bash
# One-time execution
python src/orchestrator.py

# Continuous operation
RUN_MODE=continuous python src/orchestrator.py
```

### Run Colony (Multi-Agent)

```bash
# One-time cycle
python src/colony_orchestrator.py

# Continuous operation
RUN_MODE=continuous python src/colony_orchestrator.py
```

### Run Webhook Server

```bash
python src/webhook_handler.py
```

Server runs on `http://localhost:8000`

## 📊 System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     BLOOM Backend                           │
│                 (Conversion Tracking)                       │
└────────────────────┬────────────────────────────────────────┘
                     │ Webhook: POST /conversion
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Webhook Handler                            │
│            (Receives Conversion Events)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Colony Orchestrator                         │
│          (Manages Multi-Agent Colony)                       │
└────┬───────────────────────────────────────────────┬────────┘
     │                                               │
     ▼                                               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐      ┌──────────┐
│ Agent 1  │  │ Agent 2  │  │ Agent 3  │ ...  │ Agent N  │
│ (Parent) │──│  (Child) │  │  (Child) │      │  (Child) │
└────┬─────┘  └────┬─────┘  └────┬─────┘      └────┬─────┘
     │             │              │                  │
     └─────────────┴──────────────┴──────────────────┘
                        │
                        ▼
          ┌──────────────────────────────┐
          │   Platform Integrations      │
          │  • Reddit Monitor/Strategy   │
          │  • Twitter Monitor/Strategy  │
          └──────────────────────────────┘
```

### File Structure

```
bloom-ai-agent/
├── src/
│   ├── ai_agent.py              # Core agent (commission, learning, strategies)
│   ├── reddit_integration.py    # Reddit API integration
│   ├── twitter_integration.py   # Twitter API integration
│   ├── orchestrator.py          # Single agent coordinator
│   ├── agent_reproduction.py    # Reproduction system
│   ├── colony_orchestrator.py   # Multi-agent colony manager
│   └── webhook_handler.py       # Conversion webhook receiver
├── data/                        # Runtime data (agents, genealogy)
├── logs/                        # Log files
├── demo.py                      # Interactive demonstration
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
└── README.md                    # This file
```

## 🧬 Reproduction System

### Reproduction Benchmarks

Agents reproduce when meeting ALL criteria for a level:

| Level | Total Earned | Balance | Min ROI | Days Active | Child Specialization | Child Budget |
|-------|-------------|---------|---------|-------------|---------------------|--------------|
| 1 | $500 | $200 | 2.5x | 14 | Reddit Specialist | $100 |
| 2 | $1,200 | $400 | 3.0x | 30 | Twitter Specialist | $150 |
| 3 | $2,500 | $800 | 3.5x | 45 | Content Creator | $200 |
| 4 | $5,000 | $1,500 | 4.0x | 60 | Community Engager | $300 |
| 5 | $10,000 | $3,000 | 4.5x | 90 | Paid Advertiser | $500 |
| 6 | $20,000 | $5,000 | 5.0x | 120 | Enterprise Hunter | $1,000 |

### Reproduction Process

1. **Check Eligibility**: Colony checks all agents every cycle
2. **Transfer Funds**: Parent transfers starting balance to child
3. **Apply Specialization**: Child gets specialized strategies
4. **Inherit Knowledge**: Child inherits parent's ROI history for relevant strategies
5. **Independent Operation**: Both parent and child continue autonomously

## 💰 Commission Rates

| Plan Type | Price | Commission (10%) | Enterprise Hunter (20%) |
|-----------|-------|------------------|------------------------|
| Free | $0 | $0.50 | $1.00 |
| VERIFY | $19 | $1.90 | $3.80 |
| Creator | $49/mo | $4.90 | $9.80 |
| Studio | $99/mo | $9.90 | $19.80 |
| Agency | $999/mo | $99.90 | $199.80 |

## 🎯 Marketing Strategies

### Reddit Strategies

1. **Value Comment** ($0.10)
   - Finds relevant posts in target subreddits
   - Posts helpful, non-salesy comments
   - Mentions BLOOM when relevant

2. **Educational Post** ($0.50)
   - Creates value-driven posts
   - Shares actionable tips
   - Builds authority and trust

3. **Reddit Boost** ($15.00)
   - Promotes best-performing posts
   - Paid advertising strategy

### Twitter Strategies

1. **Reply** ($0.10)
   - Responds to relevant tweets
   - Empathetic and helpful
   - Under 280 characters

2. **Thread** ($0.30)
   - Educational 3-5 tweet threads
   - Actionable content
   - Mentions BLOOM in final tweet

3. **Promoted Tweet** ($25.00)
   - Promotes best-performing tweets
   - Paid advertising strategy

### Target Audiences

**Reddit Subreddits:**
- r/ArtistLounge (487K members)
- r/WeAreTheMusicMakers (1.2M members)
- r/gamedev (1.1M members)
- r/freelance (284K members)
- r/DigitalArt (500K members)

**Twitter Keywords:**
- "art stolen AI"
- "music copyright theft"
- "protect my artwork"
- "AI scraped my art"
- "copyright infringement help"

## 📈 Learning System

### ROI Tracking

Every action tracks:
- Cost (how much spent)
- Revenue (commission earned)
- Success/failure count
- ROI history (rolling average)

### Strategy Selection Algorithm

```
Score = expected_return × mode_multiplier × freshness_boost

Where:
- expected_return = cost × recent_ROI
- mode_multiplier = varies by operating mode
- freshness_boost = bonus for untested strategies (in GROWTH/SCALE)
```

**SURVIVAL Mode:**
- Heavily penalizes unproven strategies (0.1x)
- Disables strategies with ROI < 1.5x
- Conservative, survival-focused

**GROWTH Mode:**
- New strategies get 0.5x multiplier
- Profitable strategies get 1.5x boost
- Balanced exploration/exploitation

**SCALE Mode:**
- High performers (ROI > 3x) get 2x boost
- Still tests new strategies (0.7x)
- Aggressive growth mode

## 🔗 BLOOM Integration

### UTM Tracking

All agent-shared links include tracking parameters:

```
https://bloom.com?utm_source=reddit&utm_medium=ai_agent&utm_campaign=strategy_timestamp&agent_id=agent_name
```

### Webhook Integration

BLOOM backend should POST to webhook when user converts:

**Endpoint:** `POST http://agent-server:8000/conversion`

**Payload:**
```json
{
  "agent_id": "adam",
  "plan_type": "creator",
  "source_strategy": "reddit_value_comment",
  "source_platform": "reddit",
  "conversion_path": "https://bloom.com?utm_source=reddit&utm_medium=ai_agent...",
  "user_id": "user_12345",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "agent_id": "adam",
  "commission_recorded": 4.90,
  "new_balance": 154.90,
  "total_earned": 234.50,
  "reproduction": {
    "reproduced": true,
    "child_id": "adam_child_1",
    "benchmark_level": 1,
    "child_specialization": "reddit_specialist"
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

## 🛠️ API Endpoints

### Webhook Server

- `POST /conversion` - Receive conversion notification
- `GET /health` - Health check
- `GET /status` - Colony status and stats
- `GET /agents/{agent_id}` - Get agent details
- `GET /family-tree` - Get full genealogy tree

### Example: Get Colony Status

```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "status": "operational",
  "colony_stats": {
    "colony_size": 5,
    "total_balance": 1234.56,
    "total_earned": 5678.90,
    "total_spent": 1234.00,
    "overall_roi": 4.6,
    "total_conversions": 45,
    "total_reproductions": 4,
    "generations": {"0": 1, "1": 4},
    "specializations": {
      "generalist": 1,
      "reddit_specialist": 1,
      "twitter_specialist": 1,
      "content_creator": 1,
      "community_engager": 1
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📝 Usage Examples

### Create Single Agent

```python
from src.ai_agent import BloomAIAgent

agent = BloomAIAgent(agent_id="test", initial_balance=50.0)

# Choose best strategy
choice = agent.choose_next_strategy()
if choice:
    strategy_name, strategy = choice
    agent.spend(strategy.cost_per_action, strategy_name)

# Record commission
agent.record_commission(
    amount=4.90,
    user_id="user_123",
    plan_type="creator",
    source_strategy="reddit_value_comment",
    source_platform="reddit",
    conversion_path="https://bloom.com?..."
)

# Get report
report = agent.get_performance_report()
print(f"Balance: ${report['balance']:.2f}")
print(f"ROI: {report['overall_roi']:.2f}x")
```

### Create Colony

```python
from src.colony_orchestrator import ColonyOrchestrator

# Create colony
colony = ColonyOrchestrator(
    initial_agent_id="adam",
    initial_balance=100.0
)

# Run cycle
colony.run_colony_cycle()

# Simulate conversion
colony.simulate_conversion(
    agent_id="adam",
    plan_type="creator",
    source_strategy="reddit_value_comment",
    source_platform="reddit"
)

# Check for reproductions
colony.check_reproductions()

# Get stats
stats = colony.colony.get_colony_stats()
print(f"Colony size: {stats['colony_size']}")
```

## 🔍 Monitoring & Logging

### Log Files

- `logs/agent.log` - Agent operations and decisions
- `logs/webhook.log` - Webhook events and conversions

### State Files

- `data/{agent_id}_state.json` - Individual agent state
- `data/genealogy.json` - Colony family tree
- `data/reproduction_history.json` - All reproduction events

### Example: View Family Tree

```python
from src.agent_reproduction import AgentColony

colony = AgentColony.load_colony_state('data')
tree = colony.get_family_tree()

for agent_id, info in tree.items():
    print(f"{agent_id}:")
    print(f"  Parent: {info['parent_id']}")
    print(f"  Generation: {info['generation']}")
    print(f"  Specialization: {info['specialization']}")
    print(f"  Children: {info['children']}")
```

## 🧪 Testing

Run the interactive demo to see all features:

```bash
python demo.py
```

The demo includes:
1. Basic agent operation
2. Learning system demonstration
3. Operating mode transitions
4. Cellular reproduction
5. Full colony evolution simulation

## 🤝 Contributing

This is a proprietary BLOOM system. Contact the development team for contribution guidelines.

## 📄 License

Proprietary - BLOOM Inc.

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/kimberlyflowers/bloom-ai-agent/issues
- Email: support@bloom.com

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core agent with commission tracking
- ✅ Learning system with ROI optimization
- ✅ Operating modes (SURVIVAL/GROWTH/SCALE)
- ✅ Cellular reproduction system
- ✅ Reddit & Twitter integration
- ✅ Webhook server for conversions

### Phase 2 (Planned)
- [ ] Advanced content generation with A/B testing
- [ ] Sentiment analysis for opportunity scoring
- [ ] Multi-platform expansion (LinkedIn, TikTok)
- [ ] Agent communication and coordination
- [ ] Advanced analytics dashboard

### Phase 3 (Future)
- [ ] Autonomous budget management
- [ ] Cross-agent strategy sharing
- [ ] Predictive conversion modeling
- [ ] Self-optimizing reproduction benchmarks

---

**Built with ❤️ for BLOOM by the AI Growth Team**
