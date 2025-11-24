# 🚨 PRE-DEPLOY CHECKLIST - RUN BEFORE EVERY PUSH 🚨

**MANDATORY: Run ALL checks before deploying to Railway**

---

## 1. Python Syntax Check

```bash
# Check for syntax errors
python -m py_compile src/*.py
python -m py_compile *.py
```

**Expected:** No output = success
**If errors:** Fix syntax before deploying

---

## 2. Import Check

```bash
# Check if all imports work
python -c "
import sys
sys.path.insert(0, '.')
from src.chat_server import SarahChatServer
from src.sarah_browser import SarahBrowser
from src.unified_websocket_server import UnifiedWebSocketServer
from src.vision_action_reasoner import VisionActionReasoner
print('✅ All imports successful')
"
```

**Expected:** `✅ All imports successful`
**If errors:** Fix import errors before deploying

---

## 3. Critical Files Check

```bash
# Verify critical files exist and are valid
test -f src/unified_websocket_server.py && echo "✅ WebSocket server exists" || echo "❌ Missing WebSocket server"
test -f src/chat_server.py && echo "✅ Chat server exists" || echo "❌ Missing chat server"
test -f main.py && echo "✅ Main entry point exists" || echo "❌ Missing main.py"
```

**Expected:** All ✅
**If ❌:** Don't deploy - files are missing

---

## 4. WebSocket Handler Check

```bash
# Verify WebSocket handler signature is correct
grep -q "async def handle_connection(self, websocket)" src/unified_websocket_server.py && echo "✅ WebSocket handler correct" || echo "❌ WebSocket handler has WRONG signature"
```

**Expected:** `✅ WebSocket handler correct`
**If ❌:** STOP! WebSocket handler was modified - see CRITICAL_DO_NOT_MODIFY_WEBSOCKET.md

---

## 5. Logic Check (Manual)

**Review your changes:**
- [ ] Did you add any `await` on properties (like `page.url`)?
- [ ] Are all async functions properly awaited?
- [ ] Did you test the logic flow in your head?
- [ ] Are there any edge cases that could fail?
- [ ] Did you add proper error handling?

---

## 6. Performance Check (Manual)

**Check for expensive operations:**
- [ ] Are you doing unnecessary API calls?
- [ ] Are you capturing screenshots when not needed?
- [ ] Are you doing expensive operations in loops?
- [ ] Is there a fast-path for simple cases?

---

## 7. Git Status Check

```bash
# See what you're about to deploy
git status
git diff --stat
```

**Review:**
- [ ] Are you deploying the right files?
- [ ] Did you accidentally include debug code?
- [ ] Did you touch WebSocket files? (If yes, STOP and review)

---

## 8. Commit Message Check

**Good commit message:**
```
🎯 FIX specific problem - brief description

Problem: What was broken
Fix: What you changed
Impact: What this improves
```

**Bad commit message:**
```
fixed stuff
update
changes
```

---

## 9. Railway Deploy Impact Check

**Before pushing, estimate impact:**
- **Low impact:** Bug fixes, optimization, new features (safe to deploy)
- **Medium impact:** Behavior changes, new dependencies (test carefully)
- **High impact:** WebSocket changes, API changes, architecture changes (DON'T DEPLOY without backup)

---

## 10. Rollback Plan

**Before deploying, know how to rollback:**

```bash
# If deploy breaks, rollback to last working commit:
git log --oneline -5  # Find last working commit
git revert HEAD  # Revert latest commit
git push  # Deploy rollback
```

**Keep this ready!**

---

## QUICK CHECKLIST (Run every time)

```bash
# Copy-paste this before every deploy:

echo "🔍 PRE-DEPLOY CHECKS..."
echo ""

# 1. Syntax
python -m py_compile src/*.py && echo "✅ Syntax OK" || echo "❌ SYNTAX ERROR - FIX BEFORE DEPLOY"

# 2. Imports
python -c "from src.chat_server import SarahChatServer; from src.sarah_browser import SarahBrowser; from src.unified_websocket_server import UnifiedWebSocketServer" 2>/dev/null && echo "✅ Imports OK" || echo "❌ IMPORT ERROR - FIX BEFORE DEPLOY"

# 3. WebSocket handler
grep -q "async def handle_connection(self, websocket)" src/unified_websocket_server.py && echo "✅ WebSocket OK" || echo "❌ WEBSOCKET MODIFIED - STOP!"

# 4. Critical files
test -f src/unified_websocket_server.py && test -f src/chat_server.py && test -f main.py && echo "✅ Files OK" || echo "❌ MISSING FILES"

echo ""
echo "If all ✅ = Safe to deploy"
echo "If any ❌ = FIX BEFORE DEPLOYING!"
```

---

## FAILED DEPLOY RECOVERY

**If deploy breaks production:**

1. **Immediate rollback:**
   ```bash
   git revert HEAD
   git push
   ```

2. **Check Railway logs:**
   - Look for Python errors
   - Look for import errors
   - Look for WebSocket errors

3. **Fix locally:**
   - Run pre-deploy checks
   - Fix the issue
   - Test again

4. **Redeploy:**
   - Only after all checks pass
   - Monitor Railway logs during deploy

---

**🔒 REMEMBER: WebSocket code is LOCKED - see CRITICAL_DO_NOT_MODIFY_WEBSOCKET.md**

**📊 TRACK DEPLOYS: Keep a log of what worked and what broke**

**⚡ WHEN IN DOUBT: Don't deploy. Test locally first.**
