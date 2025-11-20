# Critical Fixes Needed - Priority Order

## Issue 1: Chat Not Working (HIGHEST PRIORITY)
**Problem:** Send button disabled, can't send messages
**Root Cause:** WebSocket not connecting
**Why:** Vercel environment variable `NEXT_PUBLIC_RAILWAY_WS_URL` not set correctly
**Fix:**
- Vercel Dashboard → Settings → Environment Variables
- Add: `NEXT_PUBLIC_RAILWAY_WS_URL` = `wss://bloom-ai-agent-production.up.railway.app`
- Redeploy

**Temporary Fix in Code:**
- Add fallback to always try Railway URL even if env var missing
- Show connection status clearly to user

## Issue 2: Previous Conversations Not Showing
**Problem:** Sidebar appears empty
**Root Cause:** Code IS there (line 484-503), but might not be loading from database
**Likely Causes:**
1. Database query failing silently
2. Conversations array empty on first load
3. CSS hiding the sidebar content

**Fix:**
- Add error logging to conversation loading
- Show "No conversations yet" message when empty
- Add loading state

## Issue 3: Health Score Missing
**Problem:** User can't see health metrics
**Root Cause:** Code IS there (lines 530-556), but possibly hidden by CSS or not rendering
**Fix:**
- Health score is actually shown as "KPI Stats"
- May need to make it more prominent
- Add actual health score metric

## Issue 4: Text Visibility (Black on Navy)
**Problem:** "Ready and waiting" text can't be read
**Root Cause:** Dark text on dark background
**Where:** Screen placeholder when Sarah hasn't done anything yet
**Current colors:** #cbd5e1 (light gray) - should be visible
**Fix:**
- Increase contrast
- Use white text (#ffffff)
- Add text shadow if needed

## Issue 5: File Upload Breaks Chat
**Problem:** After uploading file, can't type in chat
**Root Cause:** Likely a state issue or focus issue
**Fix:**
- Don't clear chat input on file upload
- Return focus to input after upload
- Separate file upload state from chat state

## Root Cause Analysis:

**The MAIN issue is WebSocket connection.**
- If WebSocket doesn't connect → chatConnected = false
- If chatConnected = false → ALL inputs disabled
- This explains why user can't send messages OR type after file upload

**Fix order:**
1. WebSocket connection (fixes 80% of problems)
2. Conversation loading (make sure DB queries work)
3. Text visibility (quick CSS fix)
4. File upload state (separate concerns)

## Test Plan:
1. Open Vercel preview URL
2. Check console for errors
3. Verify WebSocket connects (look for "Connected to Sarah!")
4. Try sending a message
5. Try uploading a file
6. Try switching conversations
7. Verify all text is readable
