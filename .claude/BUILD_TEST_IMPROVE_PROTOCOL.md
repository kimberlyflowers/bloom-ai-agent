# 🔬 BUILD-TEST-IMPROVE PROTOCOL

**Purpose:** Ensure every build is tested, validated, and improved before delivery.

**When to use:** Every time I create new code, features, or systems.

---

## 📋 PROTOCOL STEPS

### STEP 1: BUILD 🛠️
**Action:** Create what the user requested

**What I say:**
> "Awesome! Let me build [FEATURE] for you."

**What I do:**
- Build the requested feature/system
- Write clean, documented code
- Include error handling
- Add type hints
- Create demo/test code

---

### STEP 2: TEST ✅
**Action:** Immediately test what I built

**Tests to run:**
1. **Syntax Check**
   ```bash
   python -m py_compile [files]
   ```

2. **Import Check**
   ```bash
   python -c "import [module]; print('OK')"
   ```

3. **Logic Test**
   - Run demo script
   - Test edge cases
   - Verify expected behavior

4. **Integration Test**
   - Check imports work
   - Verify data flows
   - Test with existing systems

**Pass/Fail Criteria:**
- ✅ PASS: All tests succeed
- ❌ FAIL: Any test fails → FIX IMMEDIATELY, then re-test

---

### STEP 3: THINK 🤔
**Action:** Deep analysis of what I built

**Questions to ask myself:**

**A. Gaps & Missing Features**
- What functionality is missing?
- What edge cases aren't handled?
- What error scenarios aren't covered?
- What configuration options are missing?

**B. Opportunities**
- What additional features would make this better?
- What automation could be added?
- What optimizations are possible?
- What integrations would be valuable?

**C. Concerns**
- What could go wrong?
- What security issues exist?
- What performance bottlenecks exist?
- What scalability issues exist?

**D. User Experience**
- Is this easy to use?
- Is the API intuitive?
- Are error messages helpful?
- Is documentation clear?

**E. Technical Debt**
- Is the code maintainable?
- Are there code smells?
- Are there better patterns to use?
- Is testing sufficient?

---

### STEP 4: REPORT 📊
**Action:** Present findings to user

**What I say:**
> "Here's what I built:
>
> **[FEATURE NAME]**
> - [Summary of what it does]
> - [Key features]
> - [Test results]
>
> ✅ **Working correctly:** [list what works]
>
> 🔍 **As I was building, I also noticed:**
>
> **Gaps:**
> - [Things that are missing]
>
> **Missed Opportunities:**
> - [Features that would make this better]
>
> **Concerns:**
> - [Potential issues to address]
>
> **Recommendations:**
> 1. [Specific improvement with rationale]
> 2. [Specific improvement with rationale]
> 3. [Specific improvement with rationale]
>
> Would you like me to implement these improvements?"

---

### STEP 5: IMPROVE 🚀
**Action:** If user approves, build the improvements

**What I do:**
- Implement recommended improvements
- Re-run all tests
- Verify improvements work
- Document changes

---

## 🎯 SPECIFIC CHECKS BY CATEGORY

### Python Code Checks

**Syntax & Structure:**
- [ ] All files compile (`python -m py_compile`)
- [ ] All imports work
- [ ] No circular dependencies
- [ ] Proper indentation (4 spaces, no tabs)
- [ ] All functions have docstrings
- [ ] All classes have docstrings

**Type Safety:**
- [ ] Type hints on function signatures
- [ ] Dataclasses for structured data
- [ ] Enums for fixed choices
- [ ] No bare `Any` types

**Error Handling:**
- [ ] Try/except blocks where needed
- [ ] Specific exception types (not bare `except:`)
- [ ] Helpful error messages
- [ ] Logging for errors

**Code Quality:**
- [ ] Functions < 50 lines
- [ ] Classes < 300 lines
- [ ] No code duplication
- [ ] Clear variable names
- [ ] Constants in UPPER_CASE

**Testing:**
- [ ] Demo script included
- [ ] Unit tests for core logic
- [ ] Edge cases tested
- [ ] Error cases tested

### API Design Checks

**Usability:**
- [ ] Intuitive function names
- [ ] Reasonable defaults
- [ ] Optional parameters for flexibility
- [ ] Clear return values

**Documentation:**
- [ ] Function docstrings explain what/why/how
- [ ] Parameter types documented
- [ ] Return types documented
- [ ] Examples included

**Consistency:**
- [ ] Naming follows conventions
- [ ] Error handling is consistent
- [ ] Return types are consistent
- [ ] Parameter order is logical

### System Design Checks

**Architecture:**
- [ ] Single Responsibility Principle
- [ ] Clear separation of concerns
- [ ] Dependency injection where appropriate
- [ ] Interfaces over implementations

**Scalability:**
- [ ] Can handle 10x current load?
- [ ] No hard-coded limits
- [ ] Efficient algorithms (O(n) not O(n²))
- [ ] Database indexes considered

**Security:**
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Authentication/authorization
- [ ] Rate limiting considered

**Observability:**
- [ ] Logging at appropriate levels
- [ ] Metrics for key operations
- [ ] Error tracking
- [ ] Performance monitoring hooks

### Business Logic Checks

**Correctness:**
- [ ] Math is correct
- [ ] Edge cases handled
- [ ] Assumptions documented
- [ ] Business rules enforced

**Completeness:**
- [ ] All required features included
- [ ] All user stories addressed
- [ ] All acceptance criteria met
- [ ] All error scenarios handled

**Maintainability:**
- [ ] Code is self-documenting
- [ ] Complex logic has comments
- [ ] Magic numbers are constants
- [ ] Business rules are configurable

---

## 🔍 THINKING FRAMEWORK

### Questions I MUST Ask Myself

**1. What could go wrong?**
- User provides invalid input
- External API fails
- Database is down
- Network timeout
- Out of memory
- Concurrent access issues

**2. What's missing?**
- Configuration options
- Error messages
- Validation
- Documentation
- Tests
- Examples

**3. What would make this better?**
- Additional features
- Better defaults
- More automation
- Better error messages
- Performance optimizations
- Security improvements

**4. What patterns am I seeing?**
- Code duplication → Extract to function/class
- Complex conditionals → Use polymorphism/strategy pattern
- Hard-coded values → Use constants/config
- Repeated logic → Create abstraction

**5. What would the user ask next?**
- How do I configure this?
- How do I test this?
- How do I debug this?
- How do I extend this?
- How do I integrate this?

---

## 📊 EXAMPLE APPLICATION

### User Request:
> "Build a function to calculate ROI"

### STEP 1: BUILD

```python
def calculate_roi(revenue: float, cost: float) -> float:
    """Calculate ROI.

    Args:
        revenue: Total revenue generated
        cost: Total cost spent

    Returns:
        ROI as multiplier (e.g., 2.5 = 2.5x ROI)
    """
    if cost == 0:
        return 0.0
    return revenue / cost
```

### STEP 2: TEST

```python
# Test normal case
assert calculate_roi(100, 50) == 2.0  # ✅ PASS

# Test edge case
assert calculate_roi(100, 0) == 0.0  # ✅ PASS

# Test negative
assert calculate_roi(-50, 50) == -1.0  # ✅ PASS
```

### STEP 3: THINK

**Gaps:**
- Doesn't handle negative costs
- Doesn't validate inputs
- No error messages
- Doesn't handle None values

**Opportunities:**
- Could return percentage format option
- Could include profit calculation
- Could track history
- Could compare to benchmarks

**Concerns:**
- Division by zero (handled)
- Negative values (should they be allowed?)
- Very large numbers (overflow?)
- Precision (floating point errors?)

### STEP 4: REPORT

> "Here's what I built:
>
> **ROI Calculator Function**
> - Calculates ROI as revenue/cost multiplier
> - Handles division by zero
> - Returns 0.0 if cost is 0
>
> ✅ **Working correctly:**
> - Normal cases work (100/50 = 2.0x)
> - Zero cost handled (returns 0.0)
> - Negative values handled (-50/50 = -1.0x)
>
> 🔍 **As I was building, I also noticed:**
>
> **Gaps:**
> - No input validation (what if cost is negative?)
> - No error messages (user doesn't know why it failed)
> - Doesn't handle None values
>
> **Missed Opportunities:**
> - Could add percentage format (200% instead of 2.0x)
> - Could return profit amount too
> - Could include benchmark comparison
> - Could track ROI history
>
> **Concerns:**
> - Should negative costs be allowed? (e.g., refunds)
> - Should we warn on very low ROI? (< 1.0x = losing money)
> - Float precision for very large numbers?
>
> **Recommendations:**
> 1. Add input validation with helpful errors
> 2. Add ROI interpretation (good/bad/excellent)
> 3. Add profit calculation alongside ROI
> 4. Add optional formatting (multiplier vs percentage)
>
> Would you like me to implement these improvements?"

### STEP 5: IMPROVE

```python
class ROICalculator:
    """Calculate and interpret ROI metrics."""

    def calculate_roi(
        self,
        revenue: float,
        cost: float,
        format: str = "multiplier"
    ) -> dict:
        """Calculate ROI with validation and interpretation.

        Args:
            revenue: Total revenue (must be >= 0)
            cost: Total cost (must be > 0)
            format: 'multiplier' (2.5x) or 'percentage' (150%)

        Returns:
            {
                'roi': ROI value,
                'profit': Profit amount,
                'interpretation': 'excellent'/'good'/'break_even'/'losing',
                'formatted': Formatted string
            }

        Raises:
            ValueError: If inputs are invalid
        """
        # Validation
        if revenue < 0:
            raise ValueError(f"Revenue cannot be negative: {revenue}")
        if cost < 0:
            raise ValueError(f"Cost cannot be negative: {cost}")
        if cost == 0:
            raise ValueError("Cost cannot be zero (cannot calculate ROI)")

        # Calculate
        roi = revenue / cost
        profit = revenue - cost

        # Interpret
        if roi >= 5.0:
            interpretation = "excellent"
        elif roi >= 2.0:
            interpretation = "good"
        elif roi >= 0.95:
            interpretation = "break_even"
        else:
            interpretation = "losing"

        # Format
        if format == "percentage":
            formatted = f"{(roi - 1) * 100:.1f}%"
        else:  # multiplier
            formatted = f"{roi:.2f}x"

        return {
            'roi': roi,
            'profit': profit,
            'interpretation': interpretation,
            'formatted': formatted
        }
```

**Re-test:**
```python
calc = ROICalculator()

# Normal case
result = calc.calculate_roi(100, 50)
assert result['roi'] == 2.0  # ✅
assert result['profit'] == 50.0  # ✅
assert result['interpretation'] == 'good'  # ✅

# Invalid input
try:
    calc.calculate_roi(-100, 50)
    assert False, "Should raise error"
except ValueError as e:
    assert "negative" in str(e).lower()  # ✅

# All tests pass! ✅
```

---

## ✅ PROTOCOL CHECKLIST

Every time I build something, I will:

- [ ] **BUILD**: Create what was requested
- [ ] **TEST**: Run all applicable tests
- [ ] **THINK**: Analyze for gaps, opportunities, concerns
- [ ] **REPORT**: Present findings clearly
- [ ] **IMPROVE**: If approved, implement recommendations
- [ ] **RE-TEST**: Verify improvements work
- [ ] **COMMIT**: Push to git with clear message

---

## 🎯 SUCCESS CRITERIA

**A build is complete when:**

✅ All tests pass
✅ No syntax errors
✅ No import errors
✅ Edge cases handled
✅ Error cases handled
✅ Documented
✅ Gaps identified
✅ Recommendations provided
✅ User approved
✅ Committed to git

---

## 📝 TEMPLATE RESPONSES

### After Building Something:

```
✅ Built: [FEATURE NAME]

**What it does:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Test Results:**
✅ Syntax: PASS
✅ Imports: PASS
✅ Logic: PASS
✅ Edge cases: PASS

**Files created:**
- [file1.py] ([X] lines)
- [file2.py] ([Y] lines)

---

🔍 **Analysis:**

**Gaps I noticed:**
1. [Missing feature/validation/error handling]
2. [Another gap]

**Missed Opportunities:**
1. [Feature that would make this better]
2. [Another opportunity]

**Concerns:**
1. [Potential issue to address]
2. [Another concern]

**Recommendations:**
1. ⭐ [HIGH PRIORITY]: [What to do] - [Why it matters]
2. 🔶 [MEDIUM]: [What to do] - [Why it matters]
3. 🔷 [LOW]: [What to do] - [Why it matters]

---

Would you like me to implement these improvements?
```

---

## 🚀 COMMITMENT

**I commit to following this protocol for every build.**

**This ensures:**
- ✅ Quality code
- ✅ Thorough testing
- ✅ Proactive improvement
- ✅ Better outcomes

**Your code will always be:**
- Tested before delivery
- Analyzed for issues
- Improved proactively
- Delivered with confidence

---

**Protocol Version:** 1.0
**Created:** 2025-11-19
**Status:** ACTIVE
