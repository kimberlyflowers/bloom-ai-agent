# 🏆 AGENT COMPETITION SYSTEM

## Natural Selection for AI Agents

The competition system adds **evolutionary pressure** to your AI agent colony. Agents compete for higher commission rates based on performance, creating a self-improving system where the best strategies naturally dominate.

---

## 🎯 The Core Concept

**Problem**: When parent agents reproduce, all children earn the same 10% commission. There's no incentive for high-performing agents to scale faster than low-performers.

**Solution**: Performance-based commission rates!

- **Elite agents** (top performers) earn **15% commission** → More budget → Take more actions → Scale faster
- **Learner agents** (poor performers) earn **8% commission** → Limited budget → Struggle to compete → Fade out

**Result**: Best strategies naturally dominate through economic pressure.

---

## 📊 Performance Tiers

Agents are ranked on a **0-100 performance score** and assigned to tiers:

| Tier | Score Range | Commission Rate | Multiplier | Impact |
|------|-------------|-----------------|------------|--------|
| 🏆 **Elite** | 90-100 | 15% | 1.5x | +50% more budget than base |
| 🥇 **Champion** | 75-89 | 12% | 1.2x | +20% more budget than base |
| 🥈 **Competitor** | 50-74 | 10% | 1.0x | Base rate (default) |
| 🥉 **Learner** | 0-49 | 8% | 0.8x | -20% budget penalty |

---

## 🧮 How Performance Score is Calculated

Performance score (0-100) is based on **4 weighted metrics**:

```python
Performance Score =
  (ROI Score × 40%) +              # Return on investment (capped at 5x)
  (Conversion Rate Score × 30%) +  # Percentage of actions that convert (capped at 10%)
  (Revenue per Action × 20%) +     # Earnings per action (capped at $50)
  (Total Revenue × 10%)            # Total commissions earned (capped at $1000)
```

### Example Calculation

**Agent "Alpha"**:
- ROI: 3.5x → ROI Score = min(3.5/5.0, 1.0) × 100 × 0.40 = **28 points**
- Conversion Rate: 8% → Conv Score = min(8/10, 1.0) × 100 × 0.30 = **24 points**
- Revenue per Action: $12 → RPA Score = min(12/50, 1.0) × 100 × 0.20 = **4.8 points**
- Total Revenue: $450 → Rev Score = min(450/1000, 1.0) × 100 × 0.10 = **4.5 points**

**Total Score**: 28 + 24 + 4.8 + 4.5 = **61.3 points** → **Competitor Tier** (10% commission)

**Agent "Beta"** (better performance):
- ROI: 4.8x → 38.4 points
- Conversion Rate: 12% → 30 points (capped at 10% = full 30)
- Revenue per Action: $25 → 10 points
- Total Revenue: $800 → 8 points

**Total Score**: 38.4 + 30 + 10 + 8 = **86.4 points** → **Champion Tier** (12% commission)

---

## 🔄 How It Works in Practice

### When Agents Take Actions

Every time an agent executes a marketing action:

```python
# Agent takes action (e.g., Reddit comment)
agent.execute_action('reddit_value_comment')  # Costs $0.10

# Colony records it for competition tracking
colony.record_agent_action(
    agent_id='alpha',
    spent=0.10,
    actions=1,
    revenue=0.0,  # No revenue yet
    conversions=0
)
```

### When Conversions Happen

When a user signs up for BLOOM (via webhook):

```python
# Base commission for this plan
base_commission = 5.00  # $50/month plan × 10%

# Get agent's performance multiplier
multiplier = competition.get_commission_multiplier('alpha')  # 1.0x (Competitor tier)

# Calculate actual commission
actual_commission = base_commission × multiplier  # $5.00

# Record revenue
colony.record_agent_action(
    agent_id='alpha',
    revenue=5.00,
    conversions=1
)
```

**Elite agent** would earn: $5.00 × 1.5 = **$7.50** (50% more!)
**Learner agent** would earn: $5.00 × 0.8 = **$4.00** (20% less)

### Competition Cycles

**Weekly Competitions** (every Monday):
- Calculate performance scores for all eligible agents (min 10 actions, 7+ days old)
- Rank agents by score
- Award tiers based on score ranges
- Announce winner and top 5

**Monthly Competitions** (every 1st of month):
- Same as weekly but stricter eligibility (min 50 actions, 14+ days old)
- Top 10 rankings announced
- Bigger celebration for the winner!

---

## 💰 Real-World Impact

### Example: 3 Agents After 1 Month

**Scenario**: Each agent converted 10 Pro plan users ($50/month each = $5 base commission)

| Agent | Tier | Multiplier | Commission per User | Total Earned | Budget for Actions |
|-------|------|------------|---------------------|--------------|-------------------|
| Alpha | Elite | 1.5x | $7.50 | $75.00 | **$75 to spend** |
| Beta | Competitor | 1.0x | $5.00 | $50.00 | $50 to spend |
| Gamma | Learner | 0.8x | $4.00 | $40.00 | $40 to spend |

**Result**:
- Alpha can take **50% more actions** than Beta
- Alpha will likely find more customers → earn even more → widen the gap
- Gamma struggles with limited budget → falls further behind
- When Alpha reproduces, it creates children with its successful strategies
- Gamma may never reach the $500 reproduction benchmark

---

## 🧬 Natural Selection in Action

### Generation 1: All agents start equal

```
adam (Generalist)
├── alpha_child_1 (Reddit Specialist) - 10% commission
├── beta_child_1 (Twitter Specialist) - 10% commission
└── gamma_child_1 (Content Creator) - 10% commission
```

### After Week 1: Performance diverges

```
Week 1 Competition Results:
1. alpha_child_1: 78 points → Champion tier (12% commission) ⬆
2. beta_child_1: 65 points → Competitor tier (10% commission) ━
3. gamma_child_1: 42 points → Learner tier (8% commission) ⬇
```

### After Month 1: Elite agent reproduces

```
adam (Generalist)
├── alpha_child_1 (Reddit Specialist) - 15% commission ⭐ Elite!
│   └── alpha_child_1_child_1 (Twitter Specialist) - 12% commission
│       (inherits successful strategies from alpha_child_1!)
├── beta_child_1 (Twitter Specialist) - 10% commission
└── gamma_child_1 (Content Creator) - 8% commission
    (may never reproduce due to limited earnings)
```

### After Month 3: Elite dominates

```
adam (Generalist)
├── alpha_child_1 (Elite, $1,200 earned)
│   ├── alpha_child_1_child_1 (Champion, $350 earned)
│   └── alpha_child_1_child_2 (Champion, $280 earned)
├── beta_child_1 (Competitor, $450 earned)
│   └── beta_child_1_child_1 (Competitor, $120 earned)
└── gamma_child_1 (Learner, $180 earned)
    (struggling to reach $500 reproduction threshold)
```

**The alpha lineage now represents 40% of colony revenue!**

---

## 🎮 Running Competitions

### Automatic (Scheduled)

Competitions run automatically:
- **Weekly**: Every Monday at midnight
- **Monthly**: 1st of each month at midnight

```python
from src.colony_orchestrator import ColonyOrchestrator

orchestrator = ColonyOrchestrator()
orchestrator.run_continuously()  # Competitions run automatically on schedule
```

### Manual (On-Demand)

```python
# Run weekly competition manually
result = orchestrator.run_weekly_competition()

print(f"Winner: {result.winner_id}")
print(f"Score: {result.winner_score}/100")
print(f"Tier: {result.winner_tier.display_name}")

# Run monthly competition
result = orchestrator.run_monthly_competition()
```

### View Leaderboard Anytime

```python
# Get current standings
leaderboard = orchestrator.colony.get_leaderboard(limit=10)

for entry in leaderboard:
    print(f"#{entry['rank']} {entry['agent_id']}: "
          f"{entry['score']:.1f} points, "
          f"{entry['tier']} tier, "
          f"{entry['commission_rate']} commission")
```

---

## 🔍 Monitoring Performance

### Check Agent Stats

```python
from src.agent_competition import AgentCompetition

competition = AgentCompetition()

# Get detailed stats for an agent
stats = competition.get_agent_stats('alpha')

print(f"Performance Score: {stats['performance_score']}/100")
print(f"Tier: {stats['tier']}")
print(f"Commission Rate: {stats['commission_rate']}")
print(f"Commission Multiplier: {stats['commission_multiplier']}x")
print(f"Metrics:")
print(f"  ROI: {stats['metrics']['roi']}")
print(f"  Conversion Rate: {stats['metrics']['conversion_rate']}")
print(f"  Revenue per Action: {stats['metrics']['revenue_per_action']}")
```

### Get Competition History

```python
# Get recent competition results
history = competition.get_competition_history(limit=5)

for comp in history:
    print(f"{comp['period_type']} competition ({comp['start_date']})")
    print(f"  Winner: {comp['winner']['agent_id']}")
    print(f"  Score: {comp['winner']['score']}")
    print(f"  Top 5: {len(comp['rankings'][:5])} agents")
```

---

## 📈 Expected Outcomes

### Week 1
- All agents start at Competitor tier (10% commission)
- After ~10+ actions each, performance diverges
- First competition reveals leaders and strugglers

### Month 1
- Clear tier separation emerges
- Elite agents earn 50% more per conversion
- Elite agents likely reproduce first
- Learner agents may still be far from $500 reproduction threshold

### Month 3
- Elite lineages dominate colony (50-60% of agents)
- Learner agents have faded out (can't compete)
- Champion tier agents form the "middle class"
- Colony overall ROI improves by 30-50%

### Month 6
- Colony self-optimizes to 3.5-4.5x average ROI
- Most agents are Champion or Elite tier
- Only the best strategies survive
- New agents (children) inherit proven strategies
- **No manual tuning required!**

---

## ⚙️ Configuration

### Eligibility Requirements

Agents must meet these criteria to compete:

**Weekly Competition**:
- Minimum 10 actions taken
- Minimum 7 days old

**Monthly Competition**:
- Minimum 50 actions taken
- Minimum 14 days old

These prevent brand-new agents from competing before they have meaningful performance data.

### Performance Weights

Want to prioritize different metrics? Edit `src/agent_competition.py`:

```python
def calculate_performance_score(self) -> float:
    # Current weights
    roi_score = min(self.roi / 5.0, 1.0) * 100 * 0.40        # 40%
    conversion_score = min(self.conversion_rate / 10.0, 1.0) * 100 * 0.30  # 30%
    rpa_score = min(self.revenue_per_action / 50.0, 1.0) * 100 * 0.20  # 20%
    revenue_score = min(self.total_revenue / 1000.0, 1.0) * 100 * 0.10  # 10%

    # Customize weights here!
    # Example: Prioritize ROI more heavily
    # roi_score = ... * 0.50  # 50%
    # conversion_score = ... * 0.25  # 25%
```

### Tier Thresholds

Want different tier ranges? Edit `PerformanceTier` enum:

```python
class PerformanceTier(Enum):
    ELITE = ("Elite", 90, 100, 1.5)      # 90-100 score, 1.5x multiplier
    CHAMPION = ("Champion", 75, 89, 1.2) # 75-89 score, 1.2x multiplier
    COMPETITOR = ("Competitor", 50, 74, 1.0)
    LEARNER = ("Learner", 0, 49, 0.8)

    # Example: Add "Master" tier above Elite
    # MASTER = ("Master", 95, 100, 1.8)
    # ELITE = ("Elite", 85, 94, 1.5)
```

---

## 🚀 Quick Start

### 1. Run the Demo

```bash
python competition_demo.py
```

This simulates:
- 4 agents competing
- 50 action cycles
- Performance divergence
- Weekly competition
- Commission rate comparison

### 2. Integrate with Your Colony

```python
from src.colony_orchestrator import ColonyOrchestrator

# Create colony (competition system included automatically)
orchestrator = ColonyOrchestrator(
    initial_agent_id="adam",
    initial_balance=100.0
)

# Run colony (competitions run automatically on schedule)
orchestrator.run_continuously()

# Or run once and check leaderboard
orchestrator.run_colony_cycle()
leaderboard = orchestrator.colony.get_leaderboard()
```

### 3. Monitor Results

Check logs for competition announcements:

```
🏆 Running weekly competition...
🎊 WEEKLY COMPETITION RESULTS 🎊
================================
Winner: alpha_child_1
Score: 92.50/100
Tier: Elite
Commission Rate: 15%

Top 5 Rankings:
  1. alpha_child_1: 92.50 points (Elite tier)
  2. beta_child_1: 78.20 points (Champion tier)
  3. gamma_child_1: 65.10 points (Competitor tier)
  ...
```

---

## 🎯 Why This Works

### 1. **Economic Pressure**
- Better agents earn more → can afford more actions → find more customers → earn even more
- Positive feedback loop for high performers
- Negative spiral for poor performers

### 2. **Reproduction Advantage**
- Elite agents reach $500, $1200, $2500 benchmarks faster
- Create more children, spreading successful strategies
- Learner agents may never reproduce

### 3. **Strategy Evolution**
- Children inherit parent's ROI knowledge
- Successful patterns propagate through lineage
- Failed patterns die out naturally

### 4. **No Manual Intervention**
- System self-optimizes
- No need to pick "winning" strategies
- Market (conversions) decides what works

---

## 📊 Comparison: With vs Without Competition

### Without Competition (Flat 10% for All)

```
Month 3:
- adam: $450 earned, 10% commission → $450 to spend
- alpha (bad strategies): $220 earned, 10% commission → $220 to spend
- beta (good strategies): $780 earned, 10% commission → $780 to spend

Problem: Both alpha and beta reproduce at same rate once they hit benchmarks.
Bad strategies spread just as fast as good ones!
```

### With Competition

```
Month 3:
- adam: $450 earned, Competitor tier (10%) → $450 to spend
- alpha (bad strategies): $220 earned, Learner tier (8%) → $176 actual → struggling
- beta (good strategies): $780 earned, Elite tier (15%) → $1,170 actual → dominating

Result: Beta reproduces 3x faster than alpha! Good strategies spread, bad ones fade.
```

---

## 🛡️ Fairness & Integrity

### All Agents Start Equal
- Everyone begins at Competitor tier (10% commission)
- No pre-determined favorites
- Performance alone determines tier

### Objective Metrics
- ROI, conversion rate, revenue are facts
- No subjective scoring
- Can't game the system (more revenue = better score)

### Dynamic Tiers
- Tiers update based on current performance
- An Elite agent that slacks off will drop to Champion/Competitor
- A Learner that improves can rise to Competitor/Champion

### Eligibility Requirements
- Prevents brand-new agents from competing prematurely
- Ensures statistically meaningful performance data
- Fair competition among mature agents

---

## ✅ Summary

The competition system transforms your agent colony from a flat democracy into a **meritocratic ecosystem** where:

1. **Performance is rewarded** - Top agents earn up to 50% more commission
2. **Poor performers struggle** - Limited budget restricts their ability to compete
3. **Best strategies spread** - Elite agents reproduce faster, passing on successful patterns
4. **Colony self-improves** - No manual optimization needed, natural selection handles it
5. **Transparent rankings** - Leaderboards show exactly who's winning and why

**Result**: A self-evolving AI agent colony that gets smarter and more profitable over time! 🚀🧬

---

## 🆘 Troubleshooting

**Q: No agents showing in leaderboard?**
A: Agents need 10+ actions and 7+ days to be eligible. Run more cycles or wait longer.

**Q: All agents have same tier?**
A: Performance hasn't diverged yet. More cycles needed for meaningful differences.

**Q: Elite agent dropped to Champion tier?**
A: Tiers are dynamic! Recent performance matters. Check their latest ROI and conversion rate.

**Q: Want to manually adjust an agent's tier?**
A: Don't! That defeats natural selection. Let performance determine tiers objectively.

**Q: Can I disable competition system?**
A: Yes, but you'll lose the natural selection benefits. All agents will earn flat 10% commission.

---

**Ready to see natural selection in action? Run `python competition_demo.py`!** 🏆
