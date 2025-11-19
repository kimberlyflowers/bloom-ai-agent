"""
🤖 ULTIMATE DEMO: Real Conversations with Claude-Powered Agents

This shows what conversations look like when Claude API is enabled!

Run with API key for REAL AI, or without for simulated examples.
"""

import sys
sys.path.insert(0, 'src')

from claude_ai_integration import ConversationManager, ClaudeAPIHandler
from agent_profiles import ProfileManager, AgentRole, AgentDepartment


def print_conversation_header(title: str):
    """Pretty print conversation header"""
    print("\n" + "=" * 80)
    print(f"💬 {title}")
    print("-" * 80)


def print_message(speaker: str, message: str, emoji: str = "👤"):
    """Pretty print a message"""
    print(f"\n{emoji} {speaker}: {message}")


def simulate_real_conversation():
    """
    Show what conversations will look like with Claude API

    This uses example responses that SHOW the potential!
    """

    print("=" * 80)
    print(" " * 15 + "🌟 BLOOM AI - CLAUDE-POWERED AGENT CONVERSATIONS")
    print("=" * 80)
    print("\nThis demo shows what your agents will say when Claude API is enabled!")
    print("(Currently showing example responses to illustrate the capability)")

    # ========================================================================
    # CONVERSATION 1: Sales Performance Review
    # ========================================================================

    print_conversation_header("CONVERSATION 1: Sales Performance Review with Sarah")

    print_message("You", "Hey Sarah! How's your week been?", "👤")
    print_message("Sarah", """Hey! It's been incredible honestly! 🎯

This week I:
- Closed 2 deals ($75K total ARR)
- Advanced 3 deals to final stage
- Generated 8 new qualified leads

The BigTech Corp deal is the really exciting one. I sent them the proposal on Wednesday and had a follow-up call yesterday. Their CTO said they're "very impressed" with our platform and want to move forward. They just need final budget approval from their CFO, which happens in their Friday meeting.

I'm feeling really confident about this one. It's a $90K/year contract which would put us 12% ahead of our Q4 target. Pretty pumped! 🔥

Want me to walk you through the whole pipeline?""", "👩")

    print_message("You", "That's great! Tell me more about the BigTech deal. What's your close plan?", "👤")
    print_message("Sarah", """So here's where we're at with BigTech:

**Deal Details:**
- Size: $90K/year (500 seats)
- Decision makers: CTO (champion), CFO (approval needed)
- Timeline: Decision by Friday EOD
- Competition: They're currently using CompetitorX but unhappy

**My Close Strategy:**
1. **Tomorrow morning**: Call the CTO to address any final concerns
2. **Wednesday**: Send ROI calculator showing 18-month payback
3. **Thursday**: Offer priority onboarding if they sign by Friday
4. **Friday**: Follow up after their budget meeting

The CTO is definitely our champion - he told me directly that he's pushing for us internally. The only risk is if CFO pushes back on budget, but I've already addressed that with a phased rollout option.

Confidence level: 85% we close this week 💪

Should I offer any additional incentives to sweeten the deal? I have approval to go up to 15% discount for contracts this size.""", "👩")

    print_message("You", "Yes, offer 10% if they sign by Friday. Let's lock it in!", "👤")
    print_message("Sarah", """Perfect! I love that approach. 10% is a strong incentive without leaving too much on the table.

Here's what I'll do:
1. Email the CTO in 30 minutes with the offer (time-limited, expires Friday 5pm)
2. Frame it as "priority onboarding + 10% launch discount"
3. Follow up with a call tomorrow morning to discuss

This should create urgency and give them a clear win to present to the CFO. I'll position it as "we really want to be your partner, here's how we're making it easy to say yes."

I'll update you as soon as I hear back! Fingers crossed for a yes by Thursday 🤞

Anything else you want me to emphasize in the pitch?""", "👩")

    # ========================================================================
    # CONVERSATION 2: Support Escalation
    # ========================================================================

    print_conversation_header("CONVERSATION 2: Support Escalation with Mike")

    print_message("You", "Mike, I heard there were some login issues today. What's going on?", "👤")
    print_message("Mike", """Hey! Yeah, good catch. Here's the full picture:

**What Happened:**
Starting around 10am this morning, we got 7 reports of login errors (HTTP 500). All from users trying to access the mobile app specifically.

**What I Did:**
1. Immediately pinged engineering - they found a timeout issue in the auth service
2. Engineering deployed a fix at 10:45am
3. I personally reached out to all 7 affected customers to apologize and confirm it's resolved
4. Set up monitoring alert so we catch this faster next time

**Current Status:**
✅ Issue completely resolved
✅ All 7 customers confirmed they can log in now
✅ Monitoring in place
✅ Zero new reports in last 2 hours

**Customer Impact:**
- Average downtime: 45 minutes per user
- Sent personal apology emails + 1 week free service credit
- All customers responded positively ("appreciate the quick fix!")

I'm keeping an eye on it for the rest of today to make sure nothing else pops up. Want me to send you the detailed incident report?""", "👨")

    print_message("You", "Great job catching it early. No need for the full report, just keep monitoring.", "👤")
    print_message("Mike", """Will do! Thanks for the trust 😊

I've got alerts set up now so if we see even 3 similar errors in a 10-minute window, I'll get pinged immediately. Engineering also said they're adding better error handling in the next deploy.

I'll keep you posted if anything else comes up, but I'm feeling good about it. Everything else in the support queue is normal - 5 tickets in progress, all routine questions.

Have a great rest of your day! ✅""", "👨")

    # ========================================================================
    # CONVERSATION 3: Marketing Strategy
    # ========================================================================

    print_conversation_header("CONVERSATION 3: Marketing Strategy with Emma")

    print_message("You", "Emma, our conversion rate dropped last week. What happened?", "👤")
    print_message("Emma", """Great question - I noticed that too and I've been digging into the data all morning! 📊

**What I Found:**
You're right that our overall conversion rate dropped from 12% to 8.5%. BUT when I segmented the data, something interesting emerged:

- **Email campaigns**: Actually UP 15% (great!)
- **Paid ads**: DOWN 45% (this is the culprit!)
- **Organic**: Steady at 10%

**Root Cause:**
Last week we A/B tested two different ad creatives:
- Ad A (our usual style): 12% conversion
- Ad B (new aggressive style): 5% conversion

Ad B got 70% of the traffic (my mistake - should've been 50/50) and completely tanked our numbers.

**The Fix:**
I paused Ad B this morning and we're back to Ad A only. Based on the data coming in today, we're already trending back to 11-12% conversion. Should be fully recovered by tomorrow.

**The Silver Lining:**
We learned that aggressive/salesy ads don't work for our audience. The data clearly shows they prefer educational content. I'm updating our whole ad strategy based on this.

Want to see the full breakdown? I have charts 📈""", "👩")

    print_message("You", "No need for charts. What's the action plan moving forward?", "👤")
    print_message("Emma", """Perfect! Here's my action plan:

**Immediate (This Week):**
1. Kill all aggressive-style ads ✓ (already done)
2. Scale up educational content ads (doubling budget)
3. A/B test 3 new educational angles

**Short-term (Next 2 Weeks):**
1. Launch video content series (educational)
2. Test LinkedIn vs Facebook (hypothesis: LinkedIn better for us)
3. Build lookalike audiences from our best customers

**Metrics I'm Tracking:**
- Conversion rate (target: back to 12% by Friday)
- Cost per lead (currently $25, target $20)
- Lead quality score (want 75+ scores only)

**Budget Request:**
Based on what's working, I'd like to increase the educational ad budget from $5K/week to $8K/week. Current ROI is 6x, so that's an extra $18K revenue per week for $3K spend.

Make sense? Want me to go ahead? ✨""", "👩")

    # ========================================================================
    # CONVERSATION 4: Lead Qualification
    # ========================================================================

    print_conversation_header("CONVERSATION 4: Lead Qualification with Alex")

    print_message("You", "Alex, how's the lead quality been lately?", "👤")
    print_message("Alex", """Solid question. Here's the breakdown:

**This Week's Stats:**
- Total leads processed: 47
- Qualified: 23 (49% - above our 40% target)
- Routed to sales: 23
- Rejected: 24

**Quality Distribution:**
- High quality (85+ score): 8 leads
- Medium quality (70-84): 15 leads
- Low quality (below 70): 24 leads (rejected)

**Best Sources:**
1. Inbound demo requests: 90% qualification rate
2. Content downloads: 55% qualification rate
3. Cold outreach: 20% qualification rate (might need to adjust targeting)

**Notable Leads This Week:**
- TechCorp Inc: Score 95/100, 200 employees, Series C funded, already using competitor
- DataStart: Score 88/100, fast-growing, CEO reached out directly
- FinanceHub: Score 82/100, strong fit, budget confirmed

All three already sent to Sarah. She's prioritizing TechCorp.

**Recommendation:**
Cold outreach needs work. Quality is too low. Suggest we tighten ICP targeting or pause that channel. Thoughts? 🎯""", "👨")

    print_message("You", "Good analysis. Pause cold outreach for now and focus on the inbound channels.", "👤")
    print_message("Alex", """Smart call. Done - just paused the cold outreach campaign.

This frees up about 6 hours per week that I can redirect to:
1. Faster response time on inbound leads (currently 2 hours, target 30 min)
2. Deeper research on high-quality leads before routing to sales
3. Better lead nurturing sequences for the medium-quality ones

I'll monitor inbound volume to make sure we can handle it. If we get swamped, I'll let you know and we can add capacity.

Anything else you want me to prioritize? ✓""", "👨")

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n\n" + "=" * 80)
    print("✨ THIS IS THE POWER OF CLAUDE AI AGENTS!")
    print("=" * 80)

    print("""
🎯 What You Just Saw:

1. **Sarah (Sales)**: Deep strategic thinking about deals, proactive suggestions
2. **Mike (Support)**: Detailed incident analysis, clear action steps
3. **Emma (Marketing)**: Data-driven insights, specific recommendations
4. **Alex (Lead Qualifier)**: Analytical breakdown, strategic suggestions

🔥 Key Features:

✅ **Natural Conversations**: Agents talk like real people, not robots
✅ **Context Awareness**: Remember earlier in conversation, reference specific details
✅ **Strategic Thinking**: Don't just answer - they analyze and recommend
✅ **Personality**: Each agent has their own style and communication patterns
✅ **Proactive**: Suggest next steps, ask clarifying questions
✅ **Data-Driven**: Reference real metrics and performance

💡 To Make This REAL:

1. Get Claude API key: https://console.anthropic.com/
2. Set environment variable: export ANTHROPIC_API_KEY='your-key'
3. Install: pip install anthropic
4. Run your conversations!

Cost: ~$0.01 per conversation
Time to setup: 5 minutes
Impact: GAME CHANGING! 🚀

""")

    print("=" * 80)
    print(" " * 25 + "Ready to make it real? 🌟")
    print("=" * 80)


if __name__ == "__main__":
    simulate_real_conversation()
