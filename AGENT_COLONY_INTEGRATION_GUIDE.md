# 🧬 Agent Colony Integration Guide

**How to integrate the 32-agent system with Sarah's chat_server.py**

This enables:
- 🎯 Sarah triggering reproduction when hitting milestones
- 👥 New agents joining the colony
- 🧠 Automatic knowledge sharing across agents
- 🌳 Family tree tracking and genealogy

---

## 📋 Integration Steps

### **STEP 1: Add Colony System to chat_server.py**

Add these imports at the top of `src/chat_server.py`:

```python
# Add to existing imports around line 20
from src.agent_reproduction import AgentColony, REPRODUCTION_BENCHMARKS
from src.agent_team_profiles import deploy_all_agents, get_agent_by_name
from src.agent_learning_network import AgentLearningNetwork, LessonType
from src.ai_agent import BloomAIAgent, Specialization
```

---

### **STEP 2: Initialize Colony in __init__**

In the `ChatServer.__init__` method (around line 40-90), add:

```python
def __init__(self, anthropic_api_key: str, port: int = 8000):
    # ... existing initialization ...

    # Initialize Agent Colony System
    self.agent_colony = AgentColony(colony_id="bloom_main")
    self.learning_network = AgentLearningNetwork()

    # Deploy Sarah as first-generation agent
    sarah_agent = BloomAIAgent(
        agent_id="sarah_001",
        initial_balance=500.0,  # Starting capital
        specialization=Specialization.GENERALIST
    )

    self.agent_colony.add_agent(
        agent=sarah_agent,
        agent_id="sarah_001",
        parent_id=None,  # First generation (no parent)
        specialization=Specialization.GENERALIST
    )

    # Deploy all 32 agent profiles (ready to join when activated)
    self.profile_manager = deploy_all_agents()

    logger.info(f"🧬 Colony initialized: {len(self.agent_colony.agents)} active agents")
    logger.info(f"👥 Profile database loaded: {len(self.profile_manager.profiles)} agent profiles")
```

---

### **STEP 3: Track Sarah's Actions for Reproduction**

After every successful action Sarah takes, record it for the colony.

In `_analyze_and_learn` method (around line 1002), add:

```python
async def _analyze_and_learn(self, sarah_response: str, action_success: bool):
    """
    Analyze Sarah's action and extract learnings
    """
    try:
        # ... existing learning code ...

        # 🧬 COLONY INTEGRATION: Track action for reproduction eligibility
        if action_success:
            # Record successful action
            revenue = 0.0  # Could calculate based on conversion
            spent = 0.10   # Estimated cost per action

            self.agent_colony.record_agent_action(
                agent_id="sarah_001",
                revenue=revenue,
                spent=spent,
                conversions=0,
                actions=1
            )

            # 🧠 KNOWLEDGE SHARING: Share learned pattern with network
            if pattern:
                self.learning_network.contribute_lesson(
                    agent_id="sarah_001",
                    lesson_type=LessonType.BEST_PRACTICE,
                    title=f"Successful {self.current_action}",
                    description=f"Pattern: {pattern.pattern_type}",
                    context=f"URL: {self.browser.current_url}",
                    success_count=1,
                    confidence=0.8
                )

                logger.info(f"🧠 Sarah shared knowledge with colony network")

        # ... rest of existing code ...
```

---

### **STEP 4: Check for Reproduction Eligibility**

Create a new method to check if Sarah can reproduce:

```python
async def _check_reproduction_eligibility(self):
    """
    Check if Sarah (or any agent) is ready to reproduce
    Returns True if reproduction occurred
    """
    reproductions = self.agent_colony.run_reproduction_cycle()

    if reproductions > 0:
        logger.info(f"🎉 {reproductions} agent(s) reproduced!")

        # Get colony stats to show growth
        stats = self.agent_colony.get_colony_stats()
        logger.info(f"🌳 Colony now has {stats['colony_size']} agents")
        logger.info(f"💰 Total earned: ${stats['total_earned']:.2f}")
        logger.info(f"📊 Overall ROI: {stats['overall_roi']:.2f}x")

        # Notify user
        await self._stream_immediate_response(
            f"🧬 REPRODUCTION EVENT! Sarah just created {reproductions} new specialized agent(s)! "
            f"Colony now has {stats['colony_size']} agents working together."
        )

        return True

    return False
```

---

### **STEP 5: Add Periodic Reproduction Checks**

Add a check after successful actions to see if reproduction should happen.

In `handle_message` after action execution (around line 770), add:

```python
# After Sarah completes an action successfully
if action_result:
    # ... existing code ...

    # 🧬 Check if Sarah is ready to reproduce
    await self._check_reproduction_eligibility()
```

---

### **STEP 6: Add Manual Reproduction Command**

Allow the user to manually trigger reproduction checks:

In `handle_message`, add a special command handler (around line 515-580):

```python
# Add after autonomous learning triggers, before conversational check

# 🧬 COLONY MANAGEMENT COMMANDS
if 'show colony' in content_lower or 'colony status' in content_lower:
    stats = self.agent_colony.get_colony_stats()

    response = f"""🌳 **BLOOM Agent Colony Status**

**Colony Size:** {stats['colony_size']} agents

**Economic Performance:**
- Total Earned: ${stats['total_earned']:.2f}
- Total Spent: ${stats['total_spent']:.2f}
- Overall ROI: {stats['overall_roi']:.2f}x
- Total Conversions: {stats['total_conversions']}

**Reproductions:** {stats['total_reproductions']} agents born

**Generations:**
"""

    for gen, count in sorted(stats['generations'].items()):
        response += f"\n- Generation {gen}: {count} agents"

    response += "\n\n**Specializations:**"
    for spec, count in sorted(stats['specializations'].items()):
        response += f"\n- {spec}: {count} agents"

    await self.send_message(websocket, {
        'type': 'sarah_message',
        'message': response
    })
    return

if 'check reproduction' in content_lower:
    # Check Sarah's reproduction eligibility
    benchmark = self.agent_colony.check_reproduction_eligibility("sarah_001")

    if benchmark:
        response = f"""🧬 **Sarah is READY to reproduce!**

**Benchmark Level {benchmark.level} Met:**
- Minimum earned: ${benchmark.min_total_earned:.2f} ✅
- Minimum balance: ${benchmark.min_balance:.2f} ✅
- Minimum ROI: {benchmark.min_roi}x ✅
- Minimum days active: {benchmark.min_days_active} ✅

**New Agent:**
- Specialization: {benchmark.child_specialization.value}
- Starting balance: ${benchmark.child_starting_balance:.2f}

Say "reproduce now" to create the new agent!
"""
    else:
        sarah = self.agent_colony.agents.get("sarah_001")
        if sarah:
            response = f"""📊 **Sarah's Progress Toward Reproduction**

**Current Stats:**
- Total earned: ${sarah.total_earned:.2f}
- Current balance: ${sarah.commission_balance:.2f}
- Total spent: ${sarah.total_spent:.2f}
- ROI: {sarah.total_earned / sarah.total_spent if sarah.total_spent > 0 else 0:.2f}x

**Next Benchmark (Level 1):**
- Need to earn: ${REPRODUCTION_BENCHMARKS[0].min_total_earned:.2f}
- Need balance: ${REPRODUCTION_BENCHMARKS[0].min_balance:.2f}
- Need ROI: {REPRODUCTION_BENCHMARKS[0].min_roi}x
- Need days active: {REPRODUCTION_BENCHMARKS[0].min_days_active}

Keep working! 💪
"""
        else:
            response = "Could not find Sarah in the colony."

    await self.send_message(websocket, {
        'type': 'sarah_message',
        'message': response
    })
    return

if 'reproduce now' in content_lower:
    benchmark = self.agent_colony.check_reproduction_eligibility("sarah_001")

    if benchmark:
        child_id = self.agent_colony.reproduce_agent("sarah_001", benchmark)

        if child_id:
            response = f"""🎉 **REPRODUCTION SUCCESSFUL!**

Sarah has created a new agent: **{child_id}**

**Child Details:**
- Specialization: {benchmark.child_specialization.value}
- Starting balance: ${benchmark.child_starting_balance:.2f}
- Generation: 1 (Sarah's child)
- Inherited knowledge: Yes ✅

The colony is growing! 🌱
"""
        else:
            response = "Reproduction failed. Sarah may not have enough balance."
    else:
        response = "Sarah is not ready to reproduce yet. Check her progress with 'check reproduction'."

    await self.send_message(websocket, {
        'type': 'sarah_message',
        'message': response
    })
    return

if 'show family tree' in content_lower:
    tree = self.agent_colony.get_family_tree()

    response = "🌳 **Agent Family Tree**\n\n"

    # Show each agent and their children
    for agent_id, data in tree.items():
        indent = "  " * data['generation']
        response += f"{indent}├─ {agent_id} ({data['specialization']})\n"
        response += f"{indent}   Balance: ${data['balance']:.2f}\n"
        response += f"{indent}   Earned: ${data['total_earned']:.2f}\n"

        if data['children']:
            response += f"{indent}   Children: {len(data['children'])}\n"

    await self.send_message(websocket, {
        'type': 'sarah_message',
        'message': response
    })
    return
```

---

### **STEP 7: Add Knowledge Query System**

Let Sarah query the knowledge network:

```python
if 'what have we learned' in content_lower or 'colony knowledge' in content_lower:
    # Get recent lessons from learning network
    lessons = self.learning_network.get_top_lessons(limit=10)

    response = "🧠 **Colony Knowledge Base**\n\n"
    response += f"Total lessons: {len(self.learning_network.lessons)}\n\n"

    if lessons:
        response += "**Top Lessons:**\n"
        for i, lesson in enumerate(lessons, 1):
            response += f"\n{i}. **{lesson.title}**\n"
            response += f"   Discovered by: {lesson.discovered_by}\n"
            response += f"   Success rate: {lesson.success_count}/{lesson.success_count + lesson.failure_count}\n"
            response += f"   Confidence: {lesson.confidence:.0%}\n"
            response += f"   Adopted by: {len(lesson.adopted_by)} agents\n"
    else:
        response += "No lessons learned yet. Keep working and learning!"

    await self.send_message(websocket, {
        'type': 'sarah_message',
        'message': response
    })
    return
```

---

### **STEP 8: Persist Colony State**

Add save/load functionality for the colony.

At the end of `start_server` method (around line 436):

```python
async def start_server(self):
    # ... existing code ...

    # Load colony state if exists
    try:
        self.agent_colony = AgentColony.load_colony_state(
            directory='data/colony',
            colony_id='bloom_main'
        )
        logger.info("✅ Loaded existing colony state")
    except:
        logger.info("🌱 Starting fresh colony")

    # ... rest of code ...
```

Add a shutdown handler to save state:

```python
async def shutdown_server(self):
    """Save colony state on shutdown"""
    try:
        self.agent_colony.save_colony_state(directory='data/colony')
        logger.info("✅ Colony state saved")
    except Exception as e:
        logger.error(f"❌ Failed to save colony state: {e}")
```

---

## 🎯 **Usage Examples**

Once integrated, users can:

### **Check Colony Status**
```
User: "show colony"
Sarah: Shows colony size, economic performance, generations, specializations
```

### **Check Reproduction Eligibility**
```
User: "check reproduction"
Sarah: Shows progress toward next benchmark or says "Ready to reproduce!"
```

### **Trigger Reproduction**
```
User: "reproduce now"
Sarah: Creates new specialized agent (if eligible)
```

### **View Family Tree**
```
User: "show family tree"
Sarah: Displays genealogy with generations, balances, children
```

### **Query Knowledge Base**
```
User: "what have we learned?"
Sarah: Shows top lessons discovered by the colony
```

---

## 📊 **Automatic Triggers**

The system will automatically:

1. **Track all actions** Sarah takes (success/failure, cost, revenue)
2. **Share knowledge** when Sarah learns new patterns
3. **Check reproduction** after successful actions
4. **Notify user** when reproduction occurs
5. **Update colony stats** in real-time
6. **Save state** on shutdown

---

## 🌳 **Reproduction Flow Example**

```
1. Sarah works → earns commission → tracks in colony
   └─> "Sarah earned $5 from successful action"

2. Sarah hits benchmark → eligible to reproduce
   └─> "Sarah has earned $500! Ready for Level 1 reproduction"

3. User triggers (or auto-triggers) reproduction
   └─> "Reproducing... creating Reddit Specialist"

4. New agent born → inherits Sarah's knowledge
   └─> "sarah_001_child_1 created with $100 startup capital"

5. Colony grows → family tree expands
   └─> "Colony now has 2 agents (Gen 0: 1, Gen 1: 1)"

6. New agent starts working → can also reproduce
   └─> Exponential growth! 🚀
```

---

## 🔥 **Advanced: Multi-Agent Coordination**

For future expansion, enable agents to work together:

```python
async def _assign_task_to_best_agent(self, task_type: str, task_description: str):
    """
    Assign a task to the most qualified agent in the colony

    Example:
        task_type = "linkedin_posting"
        → Assigns to Marcus Chen (LinkedIn Specialist)
    """
    # Find agents with relevant specialization
    candidates = []

    for agent_id, genealogy in self.agent_colony.genealogy.items():
        # Match specialization to task type
        if task_type == "linkedin" and "linkedin" in genealogy.specialization.value.lower():
            candidates.append((agent_id, genealogy))
        elif task_type == "tiktok" and "content" in genealogy.specialization.value.lower():
            candidates.append((agent_id, genealogy))
        # ... more matching logic ...

    if candidates:
        # Pick best performer
        best_agent = max(
            candidates,
            key=lambda x: self.agent_colony.agents[x[0]].total_earned
        )

        logger.info(f"🎯 Assigned {task_type} task to {best_agent[0]}")
        return best_agent[0]

    # Default to Sarah
    return "sarah_001"
```

---

## ✅ **Integration Checklist**

- [ ] Added imports to chat_server.py
- [ ] Initialized AgentColony in __init__
- [ ] Added action tracking in _analyze_and_learn
- [ ] Created _check_reproduction_eligibility method
- [ ] Added periodic reproduction checks
- [ ] Added manual colony commands
- [ ] Added knowledge query system
- [ ] Added save/load for colony state
- [ ] Tested reproduction flow
- [ ] Verified knowledge sharing
- [ ] Checked family tree display

---

## 🚀 **Next Steps After Integration**

1. **Test the system** - Create test scenarios for reproduction
2. **Monitor growth** - Watch the colony expand naturally
3. **Optimize economics** - Adjust reproduction benchmarks if needed
4. **Enable coordination** - Let agents work together on tasks
5. **Scale to production** - Deploy the full 32-agent team!

---

**The colony system is ready! Sarah can now build her team, share knowledge, and grow the agent family autonomously.** 🌸🧬

