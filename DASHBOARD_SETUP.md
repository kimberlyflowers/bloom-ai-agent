# Dashboard Setup - Connect to Railway

## The Issue You're Seeing:

Your dashboard shows:
- ❌ Chat status: **Offline** (can't type)
- ❌ Screen status: **Connecting...** (black screen)

This is because the dashboard is trying to connect to `localhost` but Sarah is running on **Railway**!

---

## Quick Fix - 3 Steps:

### Step 1: Get Your Railway URL

1. Go to https://railway.app
2. Open your Sarah project
3. Click on the deployment
4. Copy the **domain URL** (looks like: `sarah-abc123.up.railway.app`)

### Step 2: Add Environment Variable in Vercel

1. Go to https://vercel.com
2. Open your dashboard project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `NEXT_PUBLIC_RAILWAY_WS_URL`
   - **Value**: `wss://YOUR-RAILWAY-URL:8765`
     - Replace `YOUR-RAILWAY-URL` with the Railway domain from Step 1
     - **Important**: Use `wss://` (not `ws://` or `https://`)
     - **Important**: Keep the `:8765` at the end
   - Example: `wss://sarah-abc123.up.railway.app:8765`

5. Click **Save**

### Step 3: Redeploy Dashboard

1. Still in Vercel, go to **Deployments**
2. Click the **...** menu on the latest deployment
3. Click **Redeploy**
4. Wait ~2 minutes for deployment

---

## After Redeployment:

Open your dashboard and you should see:
- ✅ Chat status: **Online** (you can type!)
- ✅ Screen status depends on what Sarah is doing:
  - If Sarah is **sleeping**: Black screen (expected - she's not using browser)
  - If Sarah is **working**: You'll see her live screen!

---

## Why the Screen is Black:

Sarah sleeps for 1 hour between her daily routines. When she's sleeping:
- No browser is open
- No screen to stream
- Black screen is **expected**

When she wakes up and starts working (checking email, creating accounts, etc.), you'll see her screen live!

---

## Testing the Chat:

Once the environment variable is set and dashboard is redeployed:

1. **Check status**: Should show "Online" 🟢
2. **Type message**: "Hey Sarah!"
3. **Wait 2-3 seconds**: You'll see "..." while she thinks
4. **Get response**: Sarah responds with her personality!

Example conversation:
```
You: Hey Sarah! What are you up to?

Sarah: Hey! Right now I'm running my daily routine - checking emails
       and managing relationships. But I'm also ready to help you with
       anything TikTok or creator-related! What's on your mind? 🌸
```

---

## Troubleshooting:

### Chat still shows "Offline":

**Check:**
1. Is ANTHROPIC_API_KEY set in Railway?
2. Is the environment variable correct in Vercel?
3. Did you redeploy after adding the variable?

**Fix:**
- Check Railway logs for errors
- Verify the WebSocket URL format: `wss://domain:8765`

### Can't type in chat:

This means chat is offline. Follow the 3 steps above!

### Screen stays black:

**This is normal if:**
- Sarah is sleeping (she sleeps 1 hour between routines)
- Sarah hasn't started any browser tasks yet

**Wait for Sarah to:**
- Create a Gmail account
- Browse TikTok
- Do any web-based task

Then you'll see her screen!

---

## What You'll See When It Works:

**Live Screen:**
- When Sarah opens a browser (for Gmail, TikTok, etc.)
- You see exactly what she sees
- Updates 2 times per second
- Status shows "LIVE" 🟢

**Chat:**
- Type any message
- Sarah responds using Claude
- She has full personality and context
- She knows her background, expertise, current work
- Warm, enthusiastic, uses emojis ✨

**Together:**
- Watch Sarah work on her screen
- Ask her "What are you doing?"
- She explains in chat!
- Complete command center! 🚀

---

## Need Help?

If you're stuck:
1. Check Railway logs (see if Sarah is running)
2. Check Vercel deployment logs (see if build succeeded)
3. Check browser console (F12) for WebSocket errors
4. The error messages will tell you what's wrong!

---

**Once this is set up, you'll have the most advanced AI agent dashboard ever built!** 🎉
