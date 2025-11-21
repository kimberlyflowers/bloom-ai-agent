# 🥷 Sarah's Stealth Mode - Bot Detection Test Checklist

This checklist helps verify Sarah can bypass Google's CAPTCHA and bot detection systems.

## 📋 Testing Priority Legend
- ✅ **IMPLEMENTED** - Feature is coded and ready
- ⚠️ **PARTIAL** - Feature exists but needs improvement
- ❌ **MISSING** - Feature not yet implemented
- 🧪 **TEST REQUIRED** - Needs manual verification

---

## 1️⃣ CLICK BEHAVIOR (What Google Watches During the Click)

### A. Multi-Attempt Detection
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Single-method approach | ✅ IMPLEMENTED | Uses ONE click method only (no 7-method barrage) | Check Railway logs - should see only "🥷 STEALTH MODE" once |
| No retry on failure | ✅ IMPLEMENTED | Stops after ONE attempt (success or fail) | If stealth fails, should NOT see multiple retry attempts |
| No method switching | ✅ IMPLEMENTED | Doesn't try keyboard, then JS, then coordinates | Logs should show ONLY "stealth-click" method, never "nuclear bypass" |

**PASS CRITERIA:** Cookie dialog clicked with ZERO failed attempts logged. No "Method 1, 2, 3..." messages.

---

### B. Timing Patterns (Humans are Irregular, Bots are Consistent)
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Random think time | ✅ IMPLEMENTED | 1.2-3.5s variance before clicking | Check logs: "Human thinking time: X.XXs" - should vary each time |
| Random scroll delay | ✅ IMPLEMENTED | 0.3-0.6s after scrolling | Check logs: timing between scroll and mouse move varies |
| Random hover time | ✅ IMPLEMENTED | 0.4-1.2s pause before click | Check logs: "Hovering for X.XXs" - different each time |
| Random post-click wait | ✅ IMPLEMENTED | 0.8-1.5s after clicking | Check logs: delay after click varies |
| NO fixed 0.1s intervals | ✅ IMPLEMENTED | Removed all sleep(0.1) patterns | Search logs for "0.1" - should NOT appear in stealth mode |

**PASS CRITERIA:** Run 5 tests - all timing values should be different (not fixed).

---

### C. Mouse Movement (Humans Move Naturally, Bots Teleport)
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Move to target (not teleport) | ✅ IMPLEMENTED | Uses page.mouse.move() | Logs show "Moving mouse to (X, Y)" |
| Random click offset | ✅ IMPLEMENTED | Clicks center +/- 20% (not exact pixel) | Check coords in logs - should vary by 20% of button size |
| Bezier curve movement | ⚠️ **NEEDS IMPROVEMENT** | Should move in curves, not straight line | Currently teleports to final position instantly |
| Micro-movements (hand tremor) | ❌ MISSING | Small random wiggles during movement | Not implemented |
| Speed variation | ❌ MISSING | Accelerate/decelerate during movement | Currently instant teleport |

**PASS CRITERIA:** Click coordinates should vary by 10-30 pixels each test. **FAIL:** Mouse teleports (needs bezier curves).

---

### D. Natural User Behavior
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Scroll before clicking | ✅ IMPLEMENTED | Scrolls button into view | Logs show "Scroll button into view" |
| Hover before clicking | ✅ IMPLEMENTED | Pauses 0.4-1.2s over button | Logs show "Hovering for X.XXs" |
| Wait after clicking | ✅ IMPLEMENTED | 0.8-1.5s to see result | Post-click delay in logs |
| Read/think before action | ✅ IMPLEMENTED | 1.2-3.5s delay at start | "Human thinking time" logged |

**PASS CRITERIA:** All 4 behaviors visible in logs for each test.

---

## 2️⃣ BROWSER FINGERPRINT (What Google Checks BEFORE You Click)

### A. Headless Browser Detection
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| navigator.webdriver flag | ❌ **EXPOSED** | Playwright sets navigator.webdriver = true | Run in browser console: `console.log(navigator.webdriver)` |
| Chrome DevTools Protocol | ❌ **EXPOSED** | CDP detection in window object | Console: `console.log(window.chrome)` |
| Headless user-agent | ⚠️ PARTIAL | User-agent may contain "HeadlessChrome" | Check request headers in Railway logs |
| Missing plugin array | ❌ **EXPOSED** | navigator.plugins is empty in headless | Console: `console.log(navigator.plugins.length)` |
| Permissions inconsistency | ❌ **EXPOSED** | Notification permissions behave differently | Console: `Notification.permission` |

**FIX NEEDED:** Install `playwright-extra-plugin-stealth` or `undetected-playwright`

**PASS CRITERIA:** All console checks should match a real Chrome browser.

---

### B. Cookies & Browsing History
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Has cookies from previous sessions | ❌ MISSING | Fresh browser = suspicious | Check browser storage in DevTools |
| Has localStorage data | ❌ MISSING | Real users have cached data | Console: `localStorage.length` |
| Has cached resources | ❌ MISSING | Images/CSS should be cached | Network tab: check if resources load from cache |
| Session history exists | ❌ MISSING | history.length > 1 for real users | Console: `history.length` |
| Google tracking cookies | ❌ MISSING | No NID, 1P_JAR, CONSENT cookies | DevTools Application tab → Cookies |

**FIX NEEDED:** Use persistent browser context (save cookies between sessions)

**PASS CRITERIA:** Should have 5+ cookies from "previous browsing" before clicking.

---

### C. Browser Characteristics
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Common screen resolution | 🧪 TEST REQUIRED | Should be 1920x1080 or 1366x768 | Console: `screen.width + 'x' + screen.height` |
| Realistic viewport size | 🧪 TEST REQUIRED | Not full screen (users resize windows) | Console: `window.innerWidth + 'x' + window.innerHeight` |
| Common font list | ❌ **UNUSUAL** | Headless has limited fonts | Canvas fingerprinting detects this |
| Timezone matches IP | 🧪 TEST REQUIRED | IP location should match browser timezone | Console: `Intl.DateTimeFormat().resolvedOptions().timeZone` |
| Language headers | 🧪 TEST REQUIRED | Accept-Language should match location | Check request headers |

**FIX NEEDED:** Configure viewport to 1366x768 (most common), set realistic fonts

**PASS CRITERIA:** All values should match a typical home user in your region.

---

## 3️⃣ NETWORK & IP REPUTATION

### A. IP Address Analysis
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Residential IP (not datacenter) | ❌ **DATACENTER IP** | Railway uses cloud infrastructure | Visit ipinfo.io from Sarah's browser |
| IP geolocation consistency | 🧪 TEST REQUIRED | IP location matches browser locale | Compare IP location to browser timezone |
| Not a known VPN/proxy | ❌ **CLOUD PROVIDER** | Google flags AWS/GCP/Railway IPs | Check IP against abuse databases |
| IP has clean reputation | 🧪 TEST REQUIRED | No history of bot traffic | Check IP on abuseipdb.com |

**FIX NEEDED:** Use residential proxy service (Bright Data, Smartproxy, etc.)

**PASS CRITERIA:** IP should resolve to residential ISP, not "Railway" or "Google Cloud"

---

### B. Traffic Patterns
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| TLS fingerprint matches Chrome | ⚠️ PARTIAL | TLS handshake should look like real Chrome | Use tls.browserleaks.com |
| HTTP/2 fingerprint | ⚠️ PARTIAL | HTTP headers should match browser version | Check with browserleaks.com/http2 |
| WebRTC leak prevention | 🧪 TEST REQUIRED | Should not leak real IP | Visit browserleaks.com/webrtc |
| DNS queries look normal | 🧪 TEST REQUIRED | DNS timing matches human browsing | Monitor with Wireshark (advanced) |

**PASS CRITERIA:** All fingerprints should match legitimate Chrome 120+

---

## 4️⃣ PAGE INTERACTION PATTERNS

### A. Before Clicking Cookie Dialog
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Lands on page naturally | ⚠️ PARTIAL | Should come from Google search or link | Check Referer header (might be missing) |
| Slight delay before interaction | ✅ IMPLEMENTED | 1.2-3.5s think time | Logs show "Human thinking time" |
| Mouse movement on page | ⚠️ PARTIAL | Some movement exists | Only moves to cookie button (suspicious) |
| Scroll activity | ✅ IMPLEMENTED | Scrolls button into view | Logs confirm scrolling |
| No instant button focus | ✅ IMPLEMENTED | Doesn't instantly target accept button | Delay before detection |

**IMPROVEMENT NEEDED:** Add random mouse movements around page before clicking

**PASS CRITERIA:** Should spend 3-5 seconds on page before clicking accept.

---

### B. After Clicking Cookie Dialog
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Waits to see result | ✅ IMPLEMENTED | 0.8-1.5s post-click delay | Logs show post-click wait |
| Continues browsing naturally | ⚠️ PARTIAL | Should scroll/move mouse after | Currently may stop immediately |
| Doesn't immediately trigger CAPTCHA | 🧪 **MUST TEST** | If CAPTCHA appears = detected | Test on google.com - does CAPTCHA show? |

**PASS CRITERIA:** No CAPTCHA after clicking cookie dialog. Can proceed to search.

---

## 5️⃣ CAPTCHA RESPONSE (If Second Test Appears)

### A. Checkbox Detection
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Finds "I'm not a robot" checkbox | ✅ IMPLEMENTED | Detects "robot" keyword | Check if click_by_description() is called |
| Clicks checkbox correctly | ⚠️ **HIT TERMS BEFORE** | Previously clicked "Terms" instead | Monitor which element gets clicked |
| Doesn't retry on failure | ✅ IMPLEMENTED | One attempt only | Logs should not show retries |

**PASS CRITERIA:** Clicks ONLY the checkbox, not Terms/Help/other links.

---

### B. Image CAPTCHA Solving
| Test | Status | Description | How to Verify |
|------|--------|-------------|---------------|
| Detects image challenge | ✅ IMPLEMENTED | detect_captcha() finds it | Logs show CAPTCHA detection |
| Can see images with vision | ✅ IMPLEMENTED | Sarah has Claude vision | Screenshot confirms she sees images |
| Can identify objects (manual) | ❌ **NO AUTO-SOLVE** | User must tell her which to click | Currently requires human guidance |
| Clicks correct tiles | ⚠️ PARTIAL | Can click coordinates | Accuracy depends on instructions |

**LIMITATION:** Image CAPTCHAs require human assistance currently.

**PASS CRITERIA:** If image CAPTCHA appears, Sarah can see it and await instructions.

---

## 6️⃣ OVERALL BOT DETECTION TEST

### Test Procedure
1. **Clear all cookies/cache** in Railway deployment
2. **Navigate to google.com**
3. **Click "Alles accepteren"** cookie dialog
4. **Observe if CAPTCHA appears**
5. **If CAPTCHA appears** → Bot detection triggered
6. **If no CAPTCHA** → Stealth mode working!

### Expected Results

#### ✅ PASSING TEST:
```
1. Land on google.com
2. Cookie dialog appears (normal)
3. Sarah clicks "Alles accepteren" (stealth mode)
4. Cookie dialog disappears
5. Google homepage loads (no CAPTCHA)
6. Can search immediately
```

#### ❌ FAILING TEST:
```
1. Land on google.com
2. Cookie dialog appears
3. Sarah clicks button (stealth or nuclear)
4. "Unusual traffic detected" message
5. CAPTCHA checkbox appears ("I'm not a robot")
6. → Bot detected!
```

---

## 🎯 PRIORITY FIXES (Ordered by Impact)

### 🔴 CRITICAL (Must Fix for Google)
1. **Install stealth plugin** → Hides navigator.webdriver
2. **Use persistent browser context** → Build cookie history
3. **Residential proxy** → Avoid datacenter IP flag

### 🟡 HIGH (Improves Detection Evasion)
4. **Bezier mouse movement** → Natural cursor path
5. **Random page interactions** → Move mouse before clicking
6. **TLS fingerprint fix** → Match real Chrome

### 🟢 MEDIUM (Polish)
7. **Viewport configuration** → Common screen size (1366x768)
8. **Font fingerprinting** → Load common fonts
9. **Timezone consistency** → Match IP location

---

## 📊 Current Score: 45/100

| Category | Score | Status |
|----------|-------|--------|
| Click Behavior | 75/100 | ✅ Good - one-shot, random timing |
| Mouse Movement | 40/100 | ⚠️ Needs bezier curves |
| Browser Fingerprint | 20/100 | ❌ Headless flags exposed |
| Cookies/History | 0/100 | ❌ Fresh browser every time |
| IP Reputation | 10/100 | ❌ Datacenter IP |
| Page Interaction | 60/100 | ⚠️ Limited movement |

**Target Score for Google:** 85/100 (residential proxy + stealth plugin + persistent context)

---

## 🧪 HOW TO TEST RIGHT NOW

### Quick Test (1 minute)
```bash
# Ask Sarah to:
1. "Go to google.com"
2. "Click accept all cookies"
3. Observe: Does CAPTCHA appear?
```

### Detailed Test (5 minutes)
```bash
# In Railway logs, verify:
1. "🥷 STEALTH MODE ACTIVATED" appears
2. "Human thinking time: X.XXs" varies each test
3. NO "Method 1, Method 2, Method 3" messages
4. "✅ STEALTH SUCCESS" appears
5. NO "Unusual traffic" message from Google
```

### Fingerprint Test (Developer Mode)
```javascript
// Open Sarah's browser console and run:
console.log({
  webdriver: navigator.webdriver,           // Should be: false
  plugins: navigator.plugins.length,        // Should be: 3+
  cookieCount: document.cookie.split(';').length, // Should be: 5+
  history: history.length,                  // Should be: > 1
  screen: screen.width + 'x' + screen.height // Should be: 1920x1080 or 1366x768
});
```

---

## 📝 TESTING LOG TEMPLATE

Use this for each test run:

```
Date: _________
Sarah Version: _________

TEST 1: Cookie Dialog Click
- Stealth mode activated: YES / NO
- Click successful: YES / NO
- CAPTCHA appeared: YES / NO
- Result: PASS / FAIL

TEST 2: Browser Fingerprint
- navigator.webdriver: _________
- Cookie count: _________
- IP type: Residential / Datacenter
- Result: PASS / FAIL

TEST 3: Timing Variance
- Think time (run 1): _________
- Think time (run 2): _________
- Think time (run 3): _________
- All different: YES / NO
- Result: PASS / FAIL

OVERALL: PASS / FAIL
Notes: _______________
```

---

## 🚀 NEXT STEPS

1. **Test current stealth mode** (see Quick Test above)
2. **If CAPTCHA appears** → Implement Priority Fixes
3. **Install playwright-stealth** → Highest impact fix
4. **Add persistent browser** → Second highest impact
5. **Re-test and iterate** → Check improvement

---

**Last Updated:** 2025-11-21
**Current Status:** Stealth mode v1 deployed, awaiting test results
