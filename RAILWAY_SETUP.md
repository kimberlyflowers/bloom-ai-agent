# 🚂 RAILWAY SETUP - 5 MINUTE GUIDE
## Deploy Sarah to Production (Just Like Vercel!)

> **This is EXACTLY like deploying to Vercel, but for Python instead of JavaScript.**

---

## ⚡ STEP 1: CREATE RAILWAY ACCOUNT (2 minutes)

### 1.1 Sign Up with GitHub

1. Go to: **https://railway.app/**
2. Click: **"Start a New Project"** (or "Login" if you've been there before)
3. Click: **"Login with GitHub"**
4. GitHub will ask: "Authorize Railway?" → Click **"Authorize railway-app"**
5. You're in! 🎉

**That's it!** Railway is now connected to your GitHub account.

---

## 🔗 STEP 2: DEPLOY FROM GITHUB (1 minute)

### 2.1 Create New Project

1. You should see Railway dashboard
2. Click: **"New Project"**
3. Click: **"Deploy from GitHub repo"**
4. You'll see a list of your repos

### 2.2 Select Your Repo

1. Find: **`bloom-ai-agent`**
2. Click it
3. Railway asks: "Which branch?"
4. Select: **`claude/setup-bloom-ai-agent-01Um2vCwq8ttgL62ws2GGm1U`**
5. Click: **"Deploy"**

### 2.3 Railway Auto-Detects Everything!

Railway will:
- ✅ See `requirements.txt` → "Oh, this is Python!"
- ✅ Install all packages automatically
- ✅ Look for `main.py` to run
- ✅ Start deploying!

**Watch the magic happen!** You'll see logs scrolling.

---

## 🔑 STEP 3: ADD API KEYS (2 minutes)

Sarah needs her API keys to work! This is just like adding environment variables in Vercel.

### 3.1 Go to Variables Tab

1. In Railway, click your project (should be called "bloom-ai-agent")
2. Click the **"Variables"** tab at the top
3. You'll see an empty list

### 3.2 Add Environment Variables

Click **"+ New Variable"** for each of these:

#### Variable 1: Anthropic API Key
```
Name:  ANTHROPIC_API_KEY
Value: sk-ant-[your key from console.anthropic.com]
```

#### Variable 2: Supabase URL
```
Name:  SUPABASE_URL
Value: https://[your-project].supabase.co
```

**Where to find it:**
- Go to Supabase dashboard
- Click "Settings" (gear icon)
- Click "API"
- Copy "Project URL"

#### Variable 3: Supabase Key
```
Name:  SUPABASE_KEY
Value: eyJhbG... (long string)
```

**Where to find it:**
- Same place as URL
- Copy the "anon" "public" key (NOT the service_role key!)

### 3.3 Redeploy

After adding all 3 variables:
1. Railway will ask: "Redeploy with new variables?"
2. Click: **"Redeploy"**
3. Watch it restart!

---

## ✅ STEP 4: CHECK IF SARAH IS ALIVE! (30 seconds)

### 4.1 View Logs

1. Click **"Deployments"** tab
2. Click the latest deployment (top one)
3. Click **"View Logs"**

### 4.2 Look for These Messages

You should see:
```
🌸 Initializing Sarah Rodriguez...
✅ Sarah is fully initialized!
✅ Sarah's identity created!
🌸 Sarah Rodriguez is online!
🌅 Starting daily routine...
```

**If you see this: CONGRATS! Sarah is LIVE! 🎉**

### 4.3 If You See Errors

Common errors:

**"ModuleNotFoundError"**
- Fix: Check that `requirements.txt` has all packages
- Go to GitHub, edit `requirements.txt`, commit
- Railway auto-redeploys!

**"Could not connect to Supabase"**
- Fix: Check your SUPABASE_URL and SUPABASE_KEY are correct
- Go to Railway → Variables → Edit them
- Click "Redeploy"

**"Anthropic API error"**
- Fix: Check your ANTHROPIC_API_KEY is correct
- Make sure you have credits in your Anthropic account

---

## 🎯 WHAT JUST HAPPENED?

You now have Sarah running 24/7 in the cloud!

```
GitHub (your code)
    ↓
Railway (runs Python 24/7)
    ↓
Sarah is ALIVE!
```

**Every time you commit to GitHub:**
- Railway sees the change
- Railway rebuilds
- Railway redeploys
- Sarah gets updated automatically!

**No terminal commands needed!**

---

## 🔄 HOW TO UPDATE SARAH

### Make a Change

1. Go to GitHub repo: `bloom-ai-agent`
2. Click any `.py` file (like `main.py`)
3. Click **"Edit"** (pencil icon)
4. Make your change
5. Click **"Commit changes"**
6. Select branch: `claude/setup-bloom-ai-agent-01Um2vCwq8ttgL62ws2GGm1U`
7. Click **"Commit"**

### Auto-Deploy!

1. Go to Railway dashboard
2. You'll see: **"Deploying..."**
3. Wait 1-2 minutes
4. Check logs
5. Sarah is updated!

**This is EXACTLY like your BLOOM app workflow!**

---

## 💡 COOL RAILWAY FEATURES

### 1. Domain Name

Railway gives you a free domain:
```
https://[project].up.railway.app
```

You can visit this to see if Sarah is running (though Sarah doesn't have a web interface yet, just logs).

### 2. Metrics

Click "Metrics" tab to see:
- CPU usage
- Memory usage
- Network traffic

### 3. Auto-Scaling

If Sarah gets busy, Railway automatically scales up!

### 4. Logs Search

In logs, use the search bar to find specific messages:
- Search "ERROR" to find problems
- Search "✅" to see successes
- Search "Sarah" to see her activities

---

## 🆘 TROUBLESHOOTING

### "Build failed"

**Check:**
- Does `requirements.txt` exist?
- Are all package names spelled correctly?

**Fix:**
- Edit `requirements.txt` in GitHub
- Commit
- Railway auto-retries

### "Crashed immediately after deploy"

**Check Logs:**
- Look for the error message
- Usually it's a missing environment variable

**Fix:**
- Go to Variables tab
- Double-check all 3 variables are set
- Redeploy

### "Can't find main.py"

Railway runs `python main.py` by default.

**Check:**
- Does `main.py` exist in root of repo?
- Is it named exactly `main.py`?

**Fix:**
- Make sure `main.py` is in the root (not in a subfolder)

### "Nothing happens in logs"

**Check:**
- Did you click "Redeploy" after adding variables?
- Is the deployment status "Active"?

**Fix:**
- Click "Deployments" → Click latest → Click "Redeploy"

---

## 🎉 SUCCESS CHECKLIST

After following this guide, you should have:

- ✅ Railway account created
- ✅ GitHub repo connected
- ✅ All 3 environment variables added
- ✅ Deployment showing "Active" status
- ✅ Logs showing "🌸 Sarah Rodriguez is online!"
- ✅ Sarah running 24/7 in the cloud
- ✅ Auto-deploy on every GitHub commit

**You're now running a 24/7 AI agent in production!**

---

## 💰 RAILWAY PRICING

**Hobby Plan (what you need):**
- $5/month flat fee
- Includes $5 of usage credits
- More than enough for Sarah!

**If Sarah gets REALLY busy:**
- Upgrade to Pro ($20/month)
- Includes $20 of credits

**For now: Start with Hobby!**

---

## 📊 COMPARE TO BLOOM APP

**BLOOM App Deployment:**
```
1. Write code in GitHub
2. Connect to Vercel
3. Add environment variables
4. Deploy!
5. Auto-deploy on commits
```

**Sarah Deployment (Railway):**
```
1. Write code in GitHub
2. Connect to Railway
3. Add environment variables
4. Deploy!
5. Auto-deploy on commits
```

**IDENTICAL WORKFLOW!** 🎯

The only difference:
- Vercel = JavaScript/TypeScript (frontend)
- Railway = Python (backend)

---

## 🚀 NEXT STEPS

After Railway is set up:

1. **Deploy Dashboard** (Vercel - you know this!)
2. **Setup Gmail** (one-time auth)
3. **Watch Sarah work!**
4. **Learn video creation** (Phase 5)

You're doing amazing! Railway setup is literally 5 minutes, then Sarah is LIVE! 🌸

---

**Ready? Let's do this!**

Start here: **https://railway.app/**
