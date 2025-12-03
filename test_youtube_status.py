import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sarah_browser import SarahBrowser

async def test_youtube_status():
    """Check if Railway IP is flagged by YouTube"""

    browser = SarahBrowser(headless=True)

    try:
        await browser.start()
        print("✅ Browser started")

        print("\n🧪 Testing YouTube IP status...")

        # Navigate to YouTube homepage
        await browser.navigate("https://www.youtube.com")
        await asyncio.sleep(3)

        # Check page title
        title = await browser.page.title()
        url = browser.page.url

        print(f"\n📄 Page title: {title}")
        print(f"🔗 URL: {url}")

        # Analyze status
        if "Sign in" in title or "Log in" in title:
            status = "⚠️ FLAGGED - Login required"
            recommendation = "Need 48-hour YouTube freeze"
        elif "Fout" in title or "Error" in title:
            status = "⚠️ FLAGGED - Error page"
            recommendation = "Need 48-hour YouTube freeze"
        elif "YouTube" in title and ("Home" in title or len(title) < 50):
            status = "✅ CLEAN - Normal YouTube access"
            recommendation = "Can proceed with safety limits"
        else:
            status = f"❓ UNKNOWN - Title: {title}"
            recommendation = "Manual inspection needed"

        print(f"\n{'='*60}")
        print(f"🎯 STATUS: {status}")
        print(f"💡 RECOMMENDATION: {recommendation}")
        print(f"{'='*60}")

        # Take screenshot for visual confirmation
        try:
            screenshot = await browser.take_screenshot()
            screenshot.save("youtube_status_test.png")
            print("\n📸 Screenshot saved: youtube_status_test.png")
            print("   Open this file to visually confirm the status")
        except Exception as e:
            print(f"⚠️ Could not save screenshot: {e}")

        return status

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

    finally:
        try:
            await browser.close()
            print("\n✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(test_youtube_status())

    # Exit code based on result
    if "CLEAN" in result:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Warning/Error
