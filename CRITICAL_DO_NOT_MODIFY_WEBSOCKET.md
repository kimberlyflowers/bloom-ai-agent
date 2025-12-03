# 🚨 CRITICAL: DO NOT MODIFY WEBSOCKET CONFIGURATION 🚨

**LAST VERIFIED WORKING:** 2025-11-24

## ⚠️ LOCKED CONFIGURATION - DO NOT CHANGE ⚠️

This WebSocket setup is **VERIFIED WORKING** on Railway with websockets 12+.
**ANY MODIFICATION WILL BREAK PRODUCTION.**

---

## Working Configuration

### File: `src/unified_websocket_server.py`
- **Handler signature:** `async def handle_connection(self, websocket)`
- **NO `path` parameter** (websockets 12+ compatibility)
- **Path accessed via:** `websocket.request.path`
- **Routes:** `/chat` and `/screen`
- **Single port:** Uses Railway's `PORT` env var

### File: `main.py`
- **Unified server** on single port (Railway requirement)
- **Port:** `int(os.getenv("PORT", 8080))`
- **Initialization order:**
  1. Browser
  2. Chat server
  3. Unified WebSocket server
  4. Start server
  5. Start streaming loop

---

## Critical Handler Code (DO NOT CHANGE)

```python
async def handle_connection(self, websocket):
    """
    ⚠️ CRITICAL: Handler signature for websockets 12+
    DO NOT add 'path' parameter - it will break!
    """
    # Get path from websocket.request.path
    path = websocket.request.path
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

    try:
        if path == "/chat" or path == "/chat/":
            await self.chat_server.handle_client(websocket)
        elif path == "/screen" or path == "/screen/":
            await self.screen_streamer.handle_client(websocket)
        else:
            await websocket.send(f"Error: Unknown path '{path}'")
            await websocket.close()
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {client_id}")
```

---

## Why This Configuration Works

✅ **Websockets 12+ compatible** - No path parameter in handler
✅ **Railway compatible** - Single port with path-based routing
✅ **Vercel dashboard compatible** - Connects to /chat and /screen
✅ **Production tested** - Currently running on Railway

---

## What NOT To Do

❌ **DO NOT** add `path` parameter to `handle_connection()`
❌ **DO NOT** split into separate ports (Railway only exposes one)
❌ **DO NOT** change handler signature
❌ **DO NOT** modify path routing logic
❌ **DO NOT** change WebSocket library version
❌ **DO NOT** "optimize" or "refactor" this code

---

## If You Need To Make Changes

**STOP. DON'T.**

This configuration is locked. If you absolutely must modify:
1. Create a backup of current working files
2. Test changes locally first
3. Verify with Railway deployment
4. Verify with Vercel dashboard connection
5. Have rollback plan ready

**Better:** Leave it alone. It works.

---

## Git Commits (Working State)

Last known working commits:
- Unified WebSocket server: a072eb2
- Railway deployment: 0a776c9
- Dashboard connection: a072eb2

---

## Verification Checklist

To verify WebSocket is working:
- [ ] Railway deployment successful
- [ ] Vercel dashboard connects (no console errors)
- [ ] Chat messages send/receive
- [ ] Screen stream displays
- [ ] No "path" parameter errors in logs
- [ ] Both /chat and /screen routes work

---

**🔒 THIS CONFIGURATION IS LOCKED 🔒**
**Last verified:** 2025-11-24
**Status:** ✅ WORKING - DO NOT TOUCH
