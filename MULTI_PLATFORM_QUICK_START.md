# 🚀 MULTI-PLATFORM AI AGENT - QUICK START

## What You Have Now

A commission-driven AI agent that works across **5 bot-friendly platforms**:

| Platform | Status | Why It's Great |
|----------|--------|---------------|
| ✅ **Discord** | NEW - BEST! | Commercial bots encouraged, huge creator communities |
| ✅ **Telegram** | NEW | Built for bots, international reach, crypto/NFT creators |
| ✅ **Slack** | NEW | B2B focus, agencies, higher-value customers |
| ✅ **Twitter/X** | IMPROVED | Already built, rate-limit compliant |
| ✅ **Reddit** | KEEP | Let AI decide if it works (auto-disables if banned) |

---

## 🎯 THE BRILLIANT PART: Self-Regulation

**The AI agent automatically learns which platforms work:**

```
Week 1: Tries all platforms
Week 2: Discord → 20 signups (high ROI) ✅
        Telegram → 15 signups (high ROI) ✅
        Reddit → Banned, 0 signups (0% ROI) ❌
Week 3: Agent in SURVIVAL mode
        → Disables Reddit (ROI < 1.5x)
        → Focuses on Discord & Telegram
Week 4: Only uses high-ROI platforms automatically!
```

**You don't configure anything - the AI figures it out!**

---

## 📦 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# This installs:
# - anthropic (Claude AI)
# - discord.py (NEW!)
# - python-telegram-bot (NEW!)
# - slack-sdk (NEW!)
# - praw (Reddit)
# - tweepy (Twitter)
# - fastapi (webhooks)
```

---

## 🔑 Get API Credentials

### 1. Discord (Start Here - EASIEST!)

**Time**: 5 minutes

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it "BLOOM IP Protector"
4. Go to "Bot" tab → "Add Bot"
5. Copy the TOKEN
6. Enable these intents:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
7. Save to `.env`:

```
DISCORD_BOT_TOKEN=your_token_here
```

**Then join Discord servers:**
- Search for "digital art" servers
- Join 5-10 creator communities
- Invite your bot (use OAuth2 URL generator)

---

### 2. Telegram (5 minutes)

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow prompts to create bot
4. Copy the TOKEN
5. Save to `.env`:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

**Then join Telegram groups:**
- Search for crypto art, NFT, creator groups
- Add your bot to groups (as admin or member)

---

### 3. Slack (10 minutes - B2B focus)

1. Go to https://api.slack.com/apps
2. Create New App → "From scratch"
3. Name: "BLOOM IP Protector"
4. Enable Socket Mode (for real-time events)
5. Create App-Level Token (connections:write)
6. Install to workspace
7. Copy tokens:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

**Then join Slack workspaces:**
- Join freelance/agency Slacks
- Get admin permission to add bot

---

### 4. Twitter (Already configured!)

You already have `TWITTER_*` credentials in `.env` from the original build.

---

### 5. Reddit (Optional - Let AI decide)

You already have `REDDIT_*` credentials. The agent will automatically disable Reddit if it gets banned.

---

## 🎮 Running the Agent

### Option 1: Single Platform Test (Discord)

```python
from src.discord_integration import setup_discord_bot
from src.ai_agent import BloomAIAgent
from dotenv import load_dotenv
import os

load_dotenv()

# Create agent
agent = BloomAIAgent(agent_id="discord_test", initial_balance=50.0)

# Setup Discord
monitor = setup_discord_bot(
    token=os.getenv('DISCORD_BOT_TOKEN'),
    agent=agent
)

# Run (blocks forever, press Ctrl+C to stop)
monitor.start()
```

**What happens:**
- Bot connects to Discord
- Monitors all servers it's in
- Responds to IP-related questions
- Tracks conversions via UTM links

---

### Option 2: Multi-Platform (All At Once)

Create `run_multi_platform.py`:

```python
import os
import asyncio
from dotenv import load_dotenv
from src.ai_agent import BloomAIAgent
from src.discord_integration import setup_discord_bot
from src.telegram_integration import setup_telegram_bot
from src.slack_integration import setup_slack_bot

load_dotenv()

async def main():
    # Create agent
    agent = BloomAIAgent(agent_id="multi_platform", initial_balance=100.0)

    # Start Discord (if token exists)
    if os.getenv('DISCORD_BOT_TOKEN'):
        discord = setup_discord_bot(os.getenv('DISCORD_BOT_TOKEN'), agent)
        asyncio.create_task(discord.start())

    # Start Telegram (if token exists)
    if os.getenv('TELEGRAM_BOT_TOKEN'):
        telegram = setup_telegram_bot(os.getenv('TELEGRAM_BOT_TOKEN'), agent)
        asyncio.create_task(telegram.start())

    # Start Slack (if tokens exist)
    if os.getenv('SLACK_BOT_TOKEN') and os.getenv('SLACK_APP_TOKEN'):
        slack = setup_slack_bot(
            os.getenv('SLACK_BOT_TOKEN'),
            os.getenv('SLACK_APP_TOKEN'),
            agent
        )
        asyncio.create_task(slack.start())

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python run_multi_platform.py
```

**What happens:**
- All configured platforms run simultaneously
- Agent learns which platforms convert best
- Automatically focuses on high-ROI platforms
- Reddit auto-disables if it gets banned

---

## 📊 Monitoring Performance

### Check Agent Stats

```python
from src.ai_agent import BloomAIAgent

# Load agent
agent = BloomAIAgent.load_state('data/multi_platform_state.json')

# Get report
report = agent.get_performance_report()

print(f"Balance: ${report['balance']:.2f}")
print(f"Total Earned: ${report['total_earned']:.2f}")
print(f"ROI: {report['overall_roi']:.2f}x")

# See platform performance
for strategy in report['strategy_performance']:
    print(f"{strategy['name']}: {strategy['roi']:.2f}x ROI")
```

### Platform-Specific Stats

**Discord:**
```python
from src.discord_integration import DiscordMonitor

monitor = DiscordMonitor(token=os.getenv('DISCORD_BOT_TOKEN'))
print(f"Messages seen: {len(monitor.messages_seen)}")
print(f"Responses sent: {len(monitor.responses_sent)}")
```

---

## 🎯 Expected Results

### Week 1
- Discord: 5-10 signups
- Telegram: 3-5 signups
- Slack: 1-2 signups (higher value)
- Reddit: Maybe banned, maybe not
- **Total: 10-20 signups**

### Month 1
- Agent learns which platforms work
- Disables low-ROI platforms automatically
- Focuses budget on high-ROI platforms
- **Total: 50-100 signups**

### Month 3
- First agent reproduction
- Specialized agents for each platform
- **Total: 125+ signups/month**
- **Revenue: $650+/month commission**

---

## 🔧 Platform-Specific Notes

### Discord
- ✅ Best platform - start here
- Join art/music/gamedev servers
- Bot can post in channels (with permission)
- DMs work great for follow-up

### Telegram
- ✅ International reach
- Crypto/NFT communities huge
- Inline bot responses powerful
- Channel broadcasts reach thousands

### Slack
- ✅ B2B focus
- Higher-value customers (agencies)
- Need workspace admin approval
- Professional tone required

### Twitter
- ⚠️ Watch rate limits (50 actions/day max)
- Already working from original build
- Good for thought leadership
- Slower growth but steady

### Reddit
- ⚠️ Let agent decide
- If it works → great!
- If it gets banned → agent auto-disables it
- No manual intervention needed

---

## 💡 Pro Tips

1. **Start with Discord only** - Easiest to set up, highest ROI
2. **Add Telegram second** - International reach
3. **Add Slack third** - B2B high-value
4. **Let agent learn** - Don't micromanage, AI optimizes itself
5. **Monitor weekly** - Check which platforms convert best
6. **Scale gradually** - Add more servers/groups over time

---

## 🚨 What If Something Breaks?

### Platform gets banned?
**No problem!** Agent automatically disables it (0% ROI → disabled in SURVIVAL mode)

### Low conversions?
**Be patient!** Agent learns over 2-3 weeks. ROI improves as it learns.

### Want to disable a platform manually?
**Edit `.env`** and remove that platform's token. Agent won't use it.

---

## 📈 Scaling Strategy

### Phase 1: Single Platform (Week 1)
- Start with Discord only
- Join 5-10 servers
- Let agent learn
- Target: 10 signups

### Phase 2: Multi-Platform (Week 2-3)
- Add Telegram
- Add Slack
- Keep Twitter running
- Target: 30 signups

### Phase 3: Scale (Month 2+)
- Join more communities (20-30 total)
- Agent reproduces at $500 earned
- Specialized agents for each platform
- Target: 100+ signups/month

---

## ✅ You're Ready!

1. Install dependencies: `pip install -r requirements.txt`
2. Get Discord token (5 min): https://discord.com/developers/applications
3. Join 5 Discord servers
4. Run agent: `python run_multi_platform.py`
5. Watch it work!

**The agent does the rest automatically.** 🤖

---

## 🆘 Need Help?

Check the logs:
```bash
tail -f logs/agent.log
```

Common issues:
- **"Token invalid"** → Re-check your .env tokens
- **"No opportunities found"** → Join more communities
- **"Permission denied"** → Bot needs permissions in Discord/Slack

---

**Ready to start earning commissions? Set up Discord and GO!** 🚀
