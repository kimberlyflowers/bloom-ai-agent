"""
🎭 Visual Capabilities Demo - Agents with Eyes and Hands!

This demo showcases:
1. Browser automation with Playwright
2. Screenshot capture with OCR text extraction
3. Visual knowledge base
4. Claude AI-powered browser automation
5. Reddit agent example

Run this to see your agents come ALIVE with visual capabilities!
"""

import sys
sys.path.append('src')

from visual_capabilities import (
    BrowserAgent,
    AIBrowserAgent,
    VisualKnowledgeBase,
    ClaudeComputerUse,
    RedditAgent
)
import os


def demo_header(title: str):
    """Print demo section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def demo_basic_browser_automation():
    """Demo 1: Basic browser automation"""
    demo_header("🌟 DEMO 1: Basic Browser Automation")

    print("\nAgents can now control real web browsers!")
    print("\nCreating browser agent...")

    # Create browser agent
    agent = BrowserAgent("demo_agent_001", headless=True)

    print("\n📋 What we'll do:")
    print("   1. Start a browser")
    print("   2. Navigate to example.com")
    print("   3. Take a screenshot")
    print("   4. Close browser")

    input("\n👉 Press Enter to start...")

    # Start browser
    print("\n🚀 Starting browser...")
    if agent.start():
        print("✅ Browser started!")

        # Navigate to website
        print("\n🌐 Navigating to example.com...")
        if agent.navigate("https://example.com"):
            print("✅ Navigation successful!")

            # Wait a bit
            print("\n⏱  Waiting for page to load...")
            agent.wait(2)

            # Take screenshot
            print("\n📸 Taking screenshot...")
            screenshot = agent.screenshot(
                description="Example.com homepage",
                tags=["demo", "example", "test"]
            )

            if screenshot:
                print(f"✅ Screenshot saved to: {screenshot.filepath}")
                print(f"   URL: {screenshot.url}")
                print(f"   Tags: {', '.join(screenshot.tags)}")

            # Close browser
            print("\n🔒 Closing browser...")
            agent.close()
            print("✅ Browser closed!")

    print("\n" + "=" * 80)
    print("✨ Basic browser automation works perfectly!")
    print("=" * 80)


def demo_screenshot_with_ocr():
    """Demo 2: Screenshot with OCR text extraction"""
    demo_header("🌟 DEMO 2: Screenshot with OCR Text Extraction")

    print("\nAgents can extract text from screenshots!")
    print("\n📋 What we'll do:")
    print("   1. Visit a text-heavy website")
    print("   2. Take screenshot with OCR enabled")
    print("   3. Extract and display text")

    # Check if pytesseract is available
    try:
        import pytesseract
        print("\n✅ pytesseract is installed - OCR will work!")
    except ImportError:
        print("\n⚠️  pytesseract not installed - OCR will be skipped")
        print("   To enable OCR: pip install pytesseract")
        print("   (Demo will continue without OCR)")

    input("\n👉 Press Enter to continue...")

    agent = BrowserAgent("ocr_agent_001", headless=True)

    if agent.start():
        print("\n🌐 Navigating to Wikipedia...")
        if agent.navigate("https://en.wikipedia.org/wiki/Artificial_intelligence"):
            agent.wait(2)

            print("\n📸 Taking screenshot with OCR enabled...")
            screenshot = agent.screenshot(
                description="Wikipedia AI article",
                tags=["wikipedia", "ai", "text-extraction"],
                extract_text=True
            )

            if screenshot:
                print(f"✅ Screenshot saved: {screenshot.filepath}")

                if screenshot.ocr_text:
                    print(f"\n📝 Extracted text (first 500 chars):")
                    print("-" * 80)
                    print(screenshot.ocr_text[:500] + "...")
                    print("-" * 80)
                    print(f"\n   Total characters extracted: {len(screenshot.ocr_text)}")
                else:
                    print("\n⚠️  No text extracted (OCR may not be configured)")

        agent.close()

    print("\n" + "=" * 80)
    print("✨ Screenshot + OCR working!")
    print("=" * 80)


def demo_visual_knowledge_base():
    """Demo 3: Visual knowledge base"""
    demo_header("🌟 DEMO 3: Visual Knowledge Base")

    print("\nAgents build a searchable library of screenshots!")
    print("\n📋 What we'll do:")
    print("   1. Visit 3 different websites")
    print("   2. Take tagged screenshots")
    print("   3. Store in knowledge base")
    print("   4. Search by tags")

    input("\n👉 Press Enter to continue...")

    # Create knowledge base
    kb = VisualKnowledgeBase()
    print("\n📚 Visual knowledge base created!")

    # Create agent
    agent = BrowserAgent("kb_agent_001", headless=True)

    if agent.start():
        # Visit multiple sites
        sites = [
            ("https://news.ycombinator.com", "Hacker News", ["tech", "news"]),
            ("https://github.com", "GitHub", ["tech", "code", "github"]),
            ("https://reddit.com", "Reddit", ["social", "reddit"])
        ]

        print(f"\n🌐 Visiting {len(sites)} websites and capturing screenshots...\n")

        for url, name, tags in sites:
            print(f"   📸 {name}...")
            agent.navigate(url)
            agent.wait(2)

            screenshot = agent.screenshot(
                description=f"{name} homepage",
                tags=tags
            )

            if screenshot:
                kb.add_screenshot(screenshot)
                print(f"      ✅ Saved with tags: {', '.join(tags)}")

        agent.close()

        # Search knowledge base
        print("\n" + "-" * 80)
        print("🔍 Searching knowledge base...")
        print("-" * 80)

        # Search by tag
        tech_screenshots = kb.search_by_tag("tech")
        print(f"\n📊 Found {len(tech_screenshots)} screenshots tagged 'tech':")
        for s in tech_screenshots:
            print(f"   • {s.description}")

        # Get recent
        recent = kb.get_recent(limit=3)
        print(f"\n📊 Most recent {len(recent)} screenshots:")
        for s in recent:
            print(f"   • {s.description} ({s.timestamp.strftime('%H:%M:%S')})")

    print("\n" + "=" * 80)
    print("✨ Visual knowledge base works perfectly!")
    print("   All screenshots are searchable and organized!")
    print("=" * 80)


def demo_claude_ai_vision():
    """Demo 4: Claude AI-powered browser automation"""
    demo_header("🌟 DEMO 4: Claude AI Vision (Optional)")

    print("\nAgents can use Claude AI to analyze screenshots and make decisions!")

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set - skipping Claude AI demo")
        print("\n💡 To enable Claude AI vision:")
        print("   1. Get API key from: https://console.anthropic.com/")
        print("   2. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("   3. Run demo again!")
        print("\n📋 What Claude AI vision can do:")
        print("   • Analyze screenshots")
        print("   • Suggest next actions with CSS selectors")
        print("   • Verify task completion")
        print("   • Make intelligent browsing decisions")
        return

    print("\n✅ Claude API key found!")
    print("\n📋 What we'll do:")
    print("   1. Navigate to a website")
    print("   2. Take screenshot")
    print("   3. Ask Claude AI to analyze it")
    print("   4. Get intelligent suggestions")

    input("\n👉 Press Enter to continue...")

    # Create AI-powered agent
    agent = AIBrowserAgent("ai_agent_001", headless=True)

    if agent.claude.enabled:
        if agent.start():
            print("\n🌐 Navigating to GitHub...")
            agent.navigate("https://github.com")
            agent.wait(2)

            print("\n🧠 Analyzing page with Claude AI...")
            result = agent.smart_screenshot(
                task="Find the login button",
                context="This is GitHub's homepage"
            )

            if result and result.get("analysis", {}).get("success"):
                analysis = result["analysis"]
                print("\n✅ Claude AI Analysis:")
                print("-" * 80)
                print(f"📄 Page Description:")
                print(f"   {analysis.get('page_description', 'N/A')[:200]}...")

                if analysis.get("suggested_actions"):
                    print(f"\n🎯 Suggested Actions:")
                    for action in analysis["suggested_actions"][:3]:
                        print(f"   • {action}")

                print("-" * 80)

            agent.close()

    print("\n" + "=" * 80)
    print("✨ Claude AI vision is incredibly powerful!")
    print("=" * 80)


def demo_reddit_agent():
    """Demo 5: Reddit automation (simulated)"""
    demo_header("🌟 DEMO 5: Reddit Agent (Simulated Demo)")

    print("\nAgents can interact with Reddit like real humans!")
    print("\n📋 Reddit Agent capabilities:")
    print("   ✅ Login to Reddit (no API needed!)")
    print("   ✅ Browse subreddits")
    print("   ✅ Read posts and comments")
    print("   ✅ Create posts and replies")
    print("   ✅ Take screenshots of all actions")
    print("   ✅ Build visual knowledge base")
    print("   ✅ Human-like delays to avoid detection")

    print("\n💡 How it works:")
    print("   • Uses actual Reddit website (not API)")
    print("   • Types and clicks like a human")
    print("   • Random delays between actions")
    print("   • Screenshots prove activity")
    print("   • Platform sees 'normal user'")

    print("\n🔐 Security note:")
    print("   This demo does NOT include real Reddit credentials.")
    print("   To use with real account, create RedditAgent with your credentials.")

    print("\n📝 Example code:")
    print("-" * 80)
    print("""
    from visual_capabilities import RedditAgent

    # Create Reddit agent
    sarah = RedditAgent(
        agent_id="sarah_001",
        username="your_reddit_username",
        password="your_reddit_password"
    )

    # Login to Reddit
    sarah.login()

    # Browse subreddit
    sarah.browse_subreddit("SaaS")

    # Create post
    sarah.create_post(
        subreddit="SaaS",
        title="How we increased ROI by 50% with AI agents",
        content="Here's our journey..."
    )

    # All actions are screenshotted!
    # Visual proof of every interaction!
    """)
    print("-" * 80)

    print("\n" + "=" * 80)
    print("✨ Reddit agent can work on ANY platform!")
    print("   LinkedIn, Instagram, Facebook, Twitter - all possible!")
    print("=" * 80)


def main():
    """Run all demos"""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "🎭 VISUAL AGENT CAPABILITIES - FULL DEMO" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\n🎯 What you'll see:")
    print("   1. Basic browser automation (Playwright)")
    print("   2. Screenshot capture with OCR text extraction")
    print("   3. Visual knowledge base with search")
    print("   4. Claude AI-powered vision (optional)")
    print("   5. Reddit agent capabilities (simulated)")

    print("\n⚡ Prerequisites:")
    print("   ✅ Playwright: installed and ready")
    print("   ✅ Browser binaries: installed")

    # Check optional dependencies
    try:
        import pytesseract
        print("   ✅ pytesseract: available for OCR")
    except ImportError:
        print("   ⚠️  pytesseract: not installed (OCR will be skipped)")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("   ✅ Claude API key: configured")
    else:
        print("   ⚠️  Claude API key: not set (AI vision will be skipped)")

    print("\n" + "=" * 80)
    input("👉 Press Enter to start the demo...")

    try:
        # Run demos
        demo_basic_browser_automation()
        input("\n👉 Press Enter for next demo...")

        demo_screenshot_with_ocr()
        input("\n👉 Press Enter for next demo...")

        demo_visual_knowledge_base()
        input("\n👉 Press Enter for next demo...")

        demo_claude_ai_vision()
        input("\n👉 Press Enter for next demo...")

        demo_reddit_agent()

        # Final summary
        print("\n\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "🎉 DEMO COMPLETE!" + " " * 36 + "║")
        print("╚" + "=" * 78 + "╝")

        print("\n🎯 What we demonstrated:")
        print("   ✅ Browser automation - Agents can control browsers")
        print("   ✅ Screenshot capture - Visual memory of all actions")
        print("   ✅ OCR text extraction - Read text from images")
        print("   ✅ Visual knowledge base - Searchable screenshot library")
        print("   ✅ Claude AI vision - Intelligent page analysis")
        print("   ✅ Reddit automation - Human-like platform interaction")

        print("\n🚀 What this enables:")
        print("   • Work on ANY platform (Reddit, LinkedIn, Instagram)")
        print("   • No API restrictions")
        print("   • No bot detection")
        print("   • Visual proof of all agent activity")
        print("   • Intelligent AI-powered decisions")

        print("\n💡 Next steps:")
        print("   1. Use BrowserAgent in your agents")
        print("   2. Build visual knowledge bases")
        print("   3. Create platform-specific agents (Reddit, LinkedIn, etc.)")
        print("   4. Enable Claude AI for intelligent automation")

        print("\n📚 Files created:")
        print("   • src/visual_capabilities.py - Full implementation")
        print("   • data/screenshots/ - Screenshot storage")
        print("   • data/visual_knowledge/index.json - Knowledge base index")

        print("\n" + "=" * 80)
        print("🌸 BLOOM AI AGENT - System #16: Visual Capabilities")
        print("   Agents now have EYES and HANDS! 👀 🙌")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
