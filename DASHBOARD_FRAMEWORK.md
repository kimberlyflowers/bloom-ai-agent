# BLOOM AI Agent - Collaborative Dashboard Framework

## Visual Layout (16:9 Aspect Ratio)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BLOOM AI - Collaborative Workspace                              [Settings] │
├───────────┬─────────────────────────────────────────────────────────────────┤
│           │                                                                 │
│  SIDEBAR  │                   MAIN WORKSPACE                                │
│  300px    │                                                                 │
│           │  ┌─────────────────────────────────────────────────────────┐   │
│  ┌──────┐ │  │  AGENT SCREEN (16:9 - 1280x720px minimum)              │   │
│  │ You  │ │  │  ┌────────────────────────────────────────────────────┐ │   │
│  └──────┘ │  │  │  [Agent Name]                         🟢 Live      │ │   │
│           │  │  │  ────────────────────────────────────────────────── │ │   │
│  TEAM:    │  │  │                                                    │ │   │
│  ┌──────┐ │  │  │  📖 Reading message: "Can you help with..."       │ │   │
│  │Sarah │ │  │  │  🤔 Generating response...                        │ │   │
│  │  🟢  │ │  │  │  💬 Response ready                                │ │   │
│  └──────┘ │  │  │  📎 File uploaded: design.png                     │ │   │
│  ┌──────┐ │  │  │  🔍 Analyzing image with Vision API...            │ │   │
│  │ Alex │ │  │  │  ✅ Analysis complete                             │ │   │
│  │  🟢  │ │  │  │                                                    │ │   │
│  └──────┘ │  │  │  [Activity feed scrolls here - last 20 items]     │ │   │
│  ┌──────┐ │  │  └────────────────────────────────────────────────────┘ │   │
│  │ Maya │ │  └─────────────────────────────────────────────────────────┘   │
│  │  ⚫  │ │                                                                 │
│  └──────┘ │  ┌─────────────────────────────────────────────────────────┐   │
│           │  │  CHAT & COLLABORATION                                   │   │
│  PROJECTS:│  │  ┌────────────────┬────────────────────────────────────┐│   │
│  ────────│  │  │  CONVERSATIONS │  ACTIVE CHAT                       ││   │
│  • Website│  │  │  ────────────  │  ──────────────                   ││   │
│  • Marketing│ │  │  📁 General   │  [Agent Avatar] Sarah:             ││   │
│  • Design │  │  │  📁 Website   │  "I can help with that! Let me...  ││   │
│  • Blog   │  │  │  📁 Marketing │                                     ││   │
│           │  │  │  + New        │  [Your Avatar] You:                ││   │
│  FILES:   │  │  │                │  "Thanks! Can you also check..."   ││   │
│  ────────│  │  │  [Scroll for  │                                     ││   │
│  📎 Shared│  │  │   more chats] │  [Agent Avatar] Alex:              ││   │
│  🖼️ Images│  │  │                │  "I reviewed the design and..."    ││   │
│  📄 Docs  │  │  │                │                                     ││   │
│           │  │  │                │  ┌────────────────────────────────┐││   │
│           │  │  │                │  │ Type message...          📎 ➤ │││   │
│           │  │  │                │  └────────────────────────────────┘││   │
│           │  │  └────────────────┴────────────────────────────────────┘│   │
│           │  └─────────────────────────────────────────────────────────┘   │
│           │                                                                 │
│  [◀ ▶]   │  ┌─────────────────────────────────────────────────────────┐   │
│           │  │  SHARED FILES & PROJECTS                                │   │
│           │  │  ┌──────────┬──────────┬──────────┬──────────┐         │   │
│           │  │  │ design.  │ proposal.│ metrics. │ logo.png │ ...     │   │
│           │  │  │ png      │ pdf      │ xlsx     │          │         │   │
│           │  │  │ Sarah    │ You      │ Alex     │ Maya     │         │   │
│           │  │  └──────────┴──────────┴──────────┴──────────┘         │   │
│           │  └─────────────────────────────────────────────────────────┘   │
└───────────┴─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Sidebar (Left - 300px, Collapsible)
- **User Profile** - Your avatar, name, status
- **Team Members** - All AI agents with online status (🟢/⚫)
  - Click to open direct chat
  - See what they're working on
- **Projects** - Active workspaces
  - Each project has its own conversations
  - Agents can create new projects
- **Shared Files** - Quick access to uploads
- **Toggle Button** - Always visible to show/hide sidebar

### 2. Agent Screen (Top - 16:9 Aspect Ratio - 1280x720px min)
- **Real-time activity feed** - What the agent is doing NOW
- **Live status indicator** - 🟢 Live / 🔴 Offline
- **Activity types:**
  - 📖 Reading messages
  - 🤔 Thinking/processing
  - 💬 Responding
  - 📎 File uploads
  - 🔍 Analyzing files
  - ✅ Tasks completed
  - 🛠️ Working on projects
  - 👥 Collaborating with other agents
- **Auto-scroll** - Latest activity always visible
- **16:9 cinematic aspect ratio** - Looks professional, large enough to see detail

### 3. Chat & Collaboration (Middle)
**Left Panel: Conversations List**
- 📁 **General** - Main team chat
- 📁 **Project Chats** - One per project (Website, Marketing, etc.)
- 📁 **Direct Messages** - 1-on-1 with each agent
- 📁 **Agent-to-Agent** - Agents can start chats with each other
- ➕ **Create New** - You or agents can start new conversations

**Right Panel: Active Chat**
- **Multi-participant** - You + multiple agents in same chat
- **Agent avatars** - See who's speaking
- **Message history** - Persists across sessions
- **File sharing** - Drag & drop or click 📎
- **Real-time** - Messages appear instantly via WebSocket
- **Input field** - Always available, works offline (queues messages)

### 4. Shared Files & Projects (Bottom)
- **Grid view** - Thumbnails of all shared files
- **File types:** Images, PDFs, Documents, Spreadsheets, Videos
- **Owner tags** - See who uploaded each file
- **Click to preview** - Quick view without downloading
- **Organized by project** - Filter files by project

## Required Features for Team Collaboration

### A. Communication
1. **You ↔ Agent Chat** - Direct messaging with any agent
2. **Agent ↔ Agent Chat** - Agents can talk to each other
3. **Group Conversations** - Multi-agent projects
4. **@ Mentions** - Tag specific agents in conversations
5. **Notifications** - See when someone messages you
6. **Typing indicators** - "Sarah is typing..."

### B. Projects & Workspaces
1. **Project Creation** - You or agents can start projects
2. **Project Conversations** - Each project has dedicated chat
3. **Project Files** - All uploads tagged to projects
4. **Project Status** - Track progress, tasks, completion
5. **Project Members** - Which agents are assigned

### C. File Management
1. **File Uploads** - From you or agents
2. **File Sharing** - Share files in conversations
3. **File Analysis** - Agents automatically analyze uploads:
   - Images → Vision API descriptions
   - PDFs → Text extraction
   - Docs → Content parsing
   - Videos → Future: transcript analysis
4. **File Organization** - Grouped by project
5. **File Search** - Find files by name, type, or project
6. **File Preview** - View without downloading

### D. Real-time Updates
1. **Live Screen** - See what agents are working on
2. **WebSocket Sync** - All chats update in real-time
3. **Online Status** - Know who's available (🟢/⚫)
4. **Activity Feed** - See recent team activity
5. **Auto-save** - All conversations persist to database

### E. Database Structure Needed

```sql
-- Current: conversations + messages
-- Need to add:

-- Projects table
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_by TEXT,  -- agent_id or 'user'
  created_at TIMESTAMP,
  status TEXT       -- 'active', 'completed', 'archived'
);

-- Project members (which agents are on which projects)
CREATE TABLE project_members (
  project_id TEXT,
  agent_id TEXT,
  role TEXT,        -- 'owner', 'member'
  joined_at TIMESTAMP
);

-- Enhanced conversations (link to projects)
ALTER TABLE conversations ADD COLUMN project_id TEXT;
ALTER TABLE conversations ADD COLUMN conversation_type TEXT; -- 'general', 'project', 'direct', 'agent_chat'
ALTER TABLE conversations ADD COLUMN participants TEXT[];   -- Array of agent_ids + 'user'

-- Files table
CREATE TABLE files (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  file_type TEXT,
  file_url TEXT,
  uploaded_by TEXT,    -- agent_id or 'user'
  project_id TEXT,
  conversation_id TEXT,
  analysis_result JSONB,  -- Store Vision/PDF analysis
  uploaded_at TIMESTAMP
);

-- Agent status tracking
CREATE TABLE agent_status (
  agent_id TEXT PRIMARY KEY,
  status TEXT,         -- 'online', 'offline', 'busy'
  current_activity TEXT,
  last_seen TIMESTAMP
);
```

## Implementation Priority

1. **FIX NOW (Critical):**
   - ✅ Fix chat send button (WebSocket connection)
   - ✅ Fix conversation persistence (database saves)
   - ✅ Fix screen aspect ratio to 16:9
   - ✅ Make screen larger and properly formatted

2. **Phase 1 (Core Collaboration):**
   - Create projects system
   - Multi-agent conversations
   - Enhanced file sharing
   - Proper conversation types (general/project/direct)

3. **Phase 2 (Advanced Features):**
   - Agent-to-agent chat
   - @ Mentions
   - Typing indicators
   - File search and preview
   - Activity feed

4. **Phase 3 (Polish):**
   - Notifications
   - Project status tracking
   - File versioning
   - Export conversations
   - Mobile responsive

## Technical Stack

- **Frontend:** Next.js + React (current)
- **Backend:** FastAPI + Python (current)
- **Database:** Supabase PostgreSQL (current)
- **Real-time:** WebSockets (current)
- **File Storage:** Supabase Storage (current)
- **AI:** Anthropic Claude API (current)

## Next Steps

1. Debug and fix current issues (chat, persistence)
2. Implement 16:9 screen layout
3. Add database tables for projects and files
4. Build project creation UI
5. Enable multi-agent conversations
6. Implement file sharing system
