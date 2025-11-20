# 🔧 CHAT OFFLINE - DEBUGGING GUIDE

## Issue: Chat shows "Offline" and can't type

This guide will help you fix the WebSocket connection between your dashboard and Railway.

---

## 🎯 Quick Fix Checklist

Go through these steps **in order**:

### ✅ Step 1: Verify Railway is Running

1. Go to **Railway Dashboard** (https://railway.app)
2. Click on your **bloom-ai-agent** project
3. Check deployment status:
   - Should show **"Active"** or **"Running"**
   - If it says **"Failed"** or **"Crashed"** - go to Step 2

### ✅ Step 2: Check Railway Logs

1. In Railway, click **"View Logs"**
2. Look for these SUCCESS messages:
   ```
   🌸 Sarah Rodriguez is online!
   💬 Chat server started - ready for conversations!
   ✅ Chat server running on ws://0.0.0.0:8766
   ```

3. If you DON'T see these messages, look for **ERROR messages**:

   **Common Error #1: Missing ANTHROPIC_API_KEY**
   ```
   ⚠️ No ANTHROPIC_API_KEY - chat will not be available
   ```
   **Fix**: Go to Step 3

   **Common Error #2: Module not found**
   ```
   ModuleNotFoundError: No module named 'websockets'
   ```
   **Fix**: Go to Step 4

   **Common Error #3: Import error**
   ```
   ImportError: cannot import name 'SarahChatServer'
   ```
   **Fix**: Check that all files are pushed to GitHub

### ✅ Step 3: Set ANTHROPIC_API_KEY in Railway

1. In Railway dashboard, click **"Variables"** tab
2. Look for `ANTHROPIC_API_KEY`
3. If missing or incorrect:
   - Click **"+ New Variable"**
   - Name: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-api03-...` (your actual key)
   - Click **"Add"**
4. Railway will auto-redeploy
5. Wait 2-3 minutes for deployment
6. Go back to Step 2 and check logs again

### ✅ Step 4: Force Railway Rebuild

Sometimes dependencies don't install correctly. Force a rebuild:

1. In Railway, click **"Settings"**
2. Scroll to bottom
3. Click **"Redeploy"** button
4. Wait 2-3 minutes
5. Check logs (Step 2)

### ✅ Step 5: Get Railway WebSocket URL

You need the correct WebSocket URL for Vercel to connect:

1. In Railway, click on your deployment
2. Look for **"Domains"** section
3. You should see a URL like:
   ```
   bloom-ai-agent-production.up.railway.app
   ```
4. Your WebSocket URLs are:
   - Chat: `wss://bloom-ai-agent-production.up.railway.app:8766`
   - Screen: `wss://bloom-ai-agent-production.up.railway.app:8765`

   **IMPORTANT**: Use `wss://` (secure WebSocket), NOT `ws://`

5. **Copy this URL** - you'll need it for Step 6

### ✅ Step 6: Configure Vercel Environment Variables

1. Go to **Vercel Dashboard** (https://vercel.com)
2. Click on your **dashboard** project
3. Click **"Settings"**
4. Click **"Environment Variables"**
5. Look for `NEXT_PUBLIC_RAILWAY_WS_URL`

6. If it exists:
   - Click **"Edit"**
   - Set value to: `wss://YOUR-RAILWAY-URL.railway.app`
   - Example: `wss://bloom-ai-agent-production.up.railway.app`
   - Click **"Save"**

7. If it doesn't exist:
   - Click **"Add New"**
   - Name: `NEXT_PUBLIC_RAILWAY_WS_URL`
   - Value: `wss://YOUR-RAILWAY-URL.railway.app`
   - Select all environments (Production, Preview, Development)
   - Click **"Add"**

8. **Redeploy Vercel**:
   - Go to **"Deployments"** tab
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**
   - Wait 1-2 minutes

### ✅ Step 7: Test Connection

1. Open your dashboard in a new tab
2. Open browser console (F12 or Right-click > Inspect > Console)
3. Look for these messages:
   ```
   💬 Connecting to chat: wss://...
   💬 Connected to Sarah's chat!
   ```

4. If you see **WebSocket error**:
   ```
   ❌ Chat error: Error: WebSocket connection failed
   ```

   Then the Railway URL is wrong. Double-check Step 5 & 6.

5. If chat connects but nothing happens:
   - Type a message in chat
   - Check Railway logs for:
     ```
     💬 User: [your message]
     ```
   - This confirms bidirectional communication works

---

## 🧪 Local Testing (Optional)

Want to test locally first? Here's how:

### Test Railway Connection Locally

```bash
# Set Railway URL
export RAILWAY_WS_URL="wss://your-railway-url.railway.app:8766"

# Run test script
python test_chat_connection.py
```

If the test passes, Railway is working! Issue is with Vercel.

### Test Everything Locally

```bash
# Terminal 1: Run Sarah
python main.py

# Terminal 2: Test connection
python test_chat_connection.py

# Terminal 3: Run dashboard
cd dashboard
npm run dev
```

Open http://localhost:3000 and test chat.

If works locally but not in production:
- Issue is with Railway deployment
- Check Railway logs carefully
- Try force rebuild (Step 4)

---

## 🔍 Advanced Debugging

### Check WebSocket Port Accessibility

Railway might not be exposing the WebSocket ports correctly.

**Railway uses dynamic ports** - you can't hardcode 8766!

#### Fix: Use PORT Environment Variable

Update `main.py` to use Railway's PORT:

```python
import os

# Get port from Railway or use 8766 locally
port = int(os.getenv("PORT", "8766"))

self.chat_server = SarahChatServer(
    anthropic_api_key=anthropic_api_key,
    port=port,  # Use dynamic port
    identity_manager=self.identity
)
```

But wait - Railway only exposes ONE port (usually $PORT).

**Solution: Run both WebSocket servers on same port OR use HTTP server**

### Better Architecture: Use Single HTTP Server

Instead of two WebSocket servers (8765, 8766), use a single FastAPI server:

```python
# main.py
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

# Chat WebSocket endpoint
@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Handle chat...

# Screen WebSocket endpoint
@app.websocket("/screen")
async def screen_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Handle screen stream...

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

Then in dashboard:
```javascript
const wsUrl = `wss://your-railway-url.railway.app/chat`
```

---

## 📊 What Should Work

### Railway Logs Should Show:
```
🚀 BLOOM AI AGENT - STARTING UP
🌸 Initializing Sarah Rodriguez...
✅ Chat server initialized
✅ Sarah is fully initialized!
🌸 Sarah Rodriguez is online!
💬 Chat server started - ready for conversations!
✅ Chat server running on ws://0.0.0.0:8766
```

### Browser Console Should Show:
```
💬 Connecting to chat: wss://bloom-ai-agent-production.up.railway.app:8766
💬 Connected to Sarah's chat!
```

### Dashboard Should Show:
- Chat status: **🟢 Online** (green badge)
- Chat input enabled
- Welcome message: "Connected to Sarah! Start chatting below 🌸"

---

## 🆘 Still Not Working?

### Check These Common Mistakes:

1. **Wrong WebSocket protocol**
   - ❌ `ws://railway-url` (insecure - won't work in production)
   - ✅ `wss://railway-url` (secure - required for HTTPS sites)

2. **Port included in Vercel env var**
   - ❌ `wss://railway-url.railway.app:8766`
   - ✅ `wss://railway-url.railway.app` (Railway handles ports)

3. **Missing PORT usage in Railway**
   - Railway assigns dynamic ports
   - Must use `os.getenv("PORT")` in your code

4. **ANTHROPIC_API_KEY typo**
   - Check for extra spaces
   - Should start with `sk-ant-`
   - Copy-paste from Anthropic console

5. **Old Vercel deployment cached**
   - Must redeploy after changing env vars
   - Or wait for auto-deploy from GitHub push

---

## 🎯 The Real Issue (Most Likely)

Based on your description, the most likely issue is:

### Railway is using dynamic PORT, but code expects 8766

**Railway assigns a $PORT environment variable** (usually 8000-9000 range).

Your code starts WebSocket on 8766, but Railway only exposes $PORT.

**Fix this by**:
1. Update code to use `os.getenv("PORT", "8766")`
2. OR use FastAPI/HTTP server with WebSocket endpoints
3. OR configure Railway to expose multiple ports (not recommended)

---

## ✅ Next Steps

1. ⬜ Go through Quick Fix Checklist (Steps 1-7)
2. ⬜ Run local test if needed
3. ⬜ Update code to use Railway PORT if needed
4. ⬜ Test in browser console
5. ⬜ Confirm chat works!

**You've got this!** 🚀

Once chat shows "Online", try typing:
```
Hey Sarah! 👋
```

She should respond with her personality! ✨
