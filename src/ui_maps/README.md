# UI Maps System

## Purpose
UI maps provide cached knowledge about application interfaces, enabling 10-15x faster navigation by using CSS selectors instead of vision-based element finding.

## How It Works

### Interaction Types
Canva (and most modern web apps) use 4 types of UI interactions:

#### 1. **navigation** - Full page load with new URL
- **Examples:** Home, Templates, Brand Kit, Projects, Settings pages
- **Behavior:** URL changes, new page loads
- **Wait strategy:** `wait_for_load_state("networkidle")`
- **Code pattern:**
  ```python
  await click(element)
  await page.wait_for_load_state("networkidle")
  ```

#### 2. **sidebar** - Panel slides in from left or right
- **Examples:** Resize menu, Download panel, Share options, Editor tool panels
- **Behavior:** Sidebar overlays page, URL stays same
- **Wait strategy:** `wait_for_selector("[panel-selector]")`
- **⚠️ CRITICAL:** Do NOT wait for navigation - page doesn't reload!
- **Code pattern:**
  ```python
  await click(element)
  await page.wait_for_selector(".sidebar-panel")
  # NO navigation wait!
  ```

#### 3. **modal** - Centered dialog overlay
- **Examples:** Create menu, Invite people dialog, Confirmation dialogs
- **Behavior:** Modal appears centered, backdrop darkens page
- **Wait strategy:** `wait_for_selector("[modal-selector]")`
- **Code pattern:**
  ```python
  await click(element)
  await page.wait_for_selector(".modal-dialog")
  ```

#### 4. **inline** - Content changes in place
- **Examples:** Search results updating, Tab switching, Form inputs
- **Behavior:** Content updates without overlay
- **Wait strategy:** `wait_for_selector("[updated-content]")` or brief delay
- **Code pattern:**
  ```python
  await click(element)
  await asyncio.sleep(0.3)  # Brief animation wait
  ```

### Speed Comparison
```
Pure Vision Approach:
- Analyze screenshot: 2-4 seconds
- Find element: 1-3 seconds
- Verify and click: 1-2 seconds
- Total: 4-9 seconds per action

UI Map Approach:
- Check map: <0.1 seconds
- Direct selector click: 0.2-0.5 seconds
- Total: 0.2-0.5 seconds per action

Speedup: 10-20x faster! 🚀
```

### Fallback Strategy
```
1. Try primary selector from map
2. Try backup selector if provided
3. Try text-based search if provided
4. Fall back to vision if all selectors fail
```

## File Structure
```
ui_maps/
├── canva/
│   ├── map.json              # Complete Canva UI map
│   └── screenshots/          # 25 reference screenshots
│       ├── 01_home_main.png
│       ├── 02_home_designs.png
│       └── ... (23 more)
├── ui_map_loader.py          # Loader utility
└── README.md                 # This file
```

## Adding New Apps

### Step 1: Capture Screenshots
Take screenshots of:
- Main navigation (home, major sections)
- Editor interface (if applicable)
- Settings pages
- Common workflows
- Modal dialogs and sidebars

### Step 2: Create map.json
```json
{
  "app": "AppName",
  "last_updated": "2025-12-03",
  "interaction_patterns": {
    "full_page_navigation": ["element1", "element2"],
    "right_sidebar": ["element3"],
    "center_modal": ["element4"]
  },
  "main_navigation": {
    "element1": {
      "description": "What this does",
      "visual_cue": "How to recognize it visually",
      "selector": "CSS selector",
      "interaction_type": "navigation|sidebar|modal|inline",
      "location": "where it appears"
    }
  }
}
```

### Step 3: Update Integration
Add to `autonomous_executor.py`:
```python
if "appname.com" in url:
    app_name = "appname"
```

## Maintenance
- **Quarterly:** Check if UI has changed
- **When errors occur:** Update outdated selectors
- **When new features appear:** Add to map
- **Mark deprecated:** Don't delete old selectors immediately, mark as "deprecated"

## Current Coverage
- ✅ **Canva** - Complete (25 screenshots, 50+ elements)
- 📋 **TikTok** - Planned
- 📋 **Instagram** - Planned

## Best Practices
1. **Always include interaction_type** - Critical for proper wait strategies
2. **Provide backup selectors** - Improves reliability
3. **Add visual_cues** - Helps humans maintain the map
4. **Document workflows** - Common tasks need step-by-step guidance
5. **Screenshot everything** - Visual references age well
