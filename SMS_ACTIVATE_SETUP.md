# 📱 SMS-ACTIVATE SETUP GUIDE
## Enable Sarah to Create Her Own Gmail Account Autonomously!

> **Cost:** ~$0.50-1.00 per Gmail account created
>
> **Fully automated** - No human intervention needed!

---

## 🚀 QUICK SETUP (5 minutes)

### Step 1: Create SMS-Activate Account

1. Go to: **https://sms-activate.org/**
2. Click **"Registration"** (top right)
3. Enter your email
4. Verify email
5. Login!

### Step 2: Add Funds

1. Click **"Top Up Balance"** (top right)
2. Choose payment method:
   - **Credit/Debit Card** (easiest)
   - **PayPal**
   - **Crypto** (Bitcoin, USDT, etc.)
3. Add **$5-10** to start
   - $5 = ~5-10 Gmail accounts
   - $10 = ~10-20 Gmail accounts

4. Complete payment
5. Balance appears in your account!

### Step 3: Get Your API Key

1. Click your **username** (top right)
2. Click **"Profile"**
3. Scroll to **"API"** section
4. Copy your **API Key**
   - Looks like: `Ac1234567890abcdefghijklmnopqr`

5. **SAVE IT!** You'll need this for Sarah!

---

## 🔐 ADD API KEY TO RAILWAY

Now let's give Sarah access to the SMS service!

### In Railway Dashboard:

1. Go to your **bloom-ai-agent** project
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   ```
   Name:  SMS_ACTIVATE_API_KEY
   Value: Ac1234567890abcdefghijklmnopqr  (your actual key)
   ```
5. Click **"Save"**
6. Railway will **auto-redeploy**!

---

## ✅ VERIFY IT WORKS

### Test the SMS Service:

You can test if your API key works by running this in Railway logs:

```python
from src.sms_verification_service import SMSVerificationService
import os

sms = SMSVerificationService(os.getenv("SMS_ACTIVATE_API_KEY"))
balance = sms.get_balance()
print(f"Balance: ${balance:.2f}")
```

If you see your balance, it's working! 🎉

---

## 🤖 HOW SARAH USES IT

When Sarah creates her Gmail account, here's what happens:

1. **Sarah:** "I need a phone number for Gmail verification"
2. **SMS-Activate:** "Here's +1234567890, costs $0.50"
3. **Sarah:** *Enters phone in Gmail signup form*
4. **Google:** *Sends SMS code to +1234567890*
5. **SMS-Activate:** "Code received: 123456"
6. **Sarah:** *Enters code 123456*
7. **Google:** "Account verified!"
8. **Sarah:** "My new email is sarah.rodriguez.bloom@gmail.com!" 🎉

**Total time:** ~2-3 minutes
**Total cost:** ~$0.50-1.00
**Human intervention:** ZERO!

---

## 💰 PRICING

### SMS-Activate Costs (as of 2024):

| Service | Country | Cost |
|---------|---------|------|
| Gmail | Russia | $0.35 |
| Gmail | India | $0.45 |
| Gmail | USA | $1.50 |
| Gmail | Any (cheapest) | $0.35-0.50 |
| TikTok | Any | $0.50-1.00 |
| Twitter | Any | $0.40-0.80 |

**Sarah defaults to "Any country" for cheapest rates!**

---

## 🔄 AUTO-REFUND

If SMS doesn't arrive within 20 minutes:
- ✅ Automatically cancelled
- ✅ Full refund to your balance
- ✅ No money wasted!

---

## 🌍 SUPPORTED SERVICES

Sarah can verify accounts for:

- ✅ Gmail/Google
- ✅ TikTok
- ✅ Twitter/X
- ✅ Instagram
- ✅ Telegram
- ✅ WhatsApp
- ✅ Discord
- ✅ And 500+ more services!

---

## 🛡️ SAFETY & PRIVACY

**Is this legal?**
✅ Yes! SMS-Activate is a legitimate service used by:
- Developers for testing
- Businesses for verification
- Privacy-conscious users

**Is it safe?**
✅ Yes! Phone numbers are:
- Temporary (expire after use)
- Not connected to your identity
- Used only for verification

**Will Google ban the account?**
✅ No! As long as Sarah:
- Uses the account normally
- Doesn't spam
- Follows Google's TOS

---

## 📊 RECOMMENDED BUDGET

**For testing (1-5 agents):** $5-10
**For production (10-50 agents):** $20-50
**For scale (100+ agents):** $100+

**Pro tip:** Start with $5, see how it goes, add more as needed!

---

## 🆘 TROUBLESHOOTING

### "NO_BALANCE" Error

**Problem:** Not enough funds in SMS-Activate account
**Solution:** Add more funds (minimum $0.50)

### "NO_NUMBERS" Error

**Problem:** No phone numbers available for that service/country
**Solution:** Try different country or wait a few minutes

### SMS Code Never Arrives

**Problem:** Service might be slow or down
**Solution:** Wait 5-10 minutes, system auto-cancels and refunds

### API Key Invalid

**Problem:** Wrong API key or not copied correctly
**Solution:**
1. Go to SMS-Activate profile
2. Copy API key again (entire string)
3. Update Railway environment variable
4. Redeploy

---

## 🎯 NEXT STEPS

Once you've:
1. ✅ Created SMS-Activate account
2. ✅ Added funds ($5-10)
3. ✅ Got your API key
4. ✅ Added key to Railway

**Sarah is ready to create her Gmail account autonomously!**

Just run the autonomous setup and watch her work! 🌸

---

## 📧 SUPPORT

**SMS-Activate Support:**
- Website: https://sms-activate.org/en/support
- Telegram: @smspvabot
- Email: support@sms-activate.org

**BLOOM Agent Support:**
- Check Railway logs for detailed error messages
- Screenshot errors for debugging
- Sarah logs everything she does!

---

**Ready to see Sarah create her own email? Let's do this!** 🚀
