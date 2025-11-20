"""
Test Chat Server Connection
Run this to diagnose WebSocket connection issues
"""

import asyncio
import websockets
import json
import os

async def test_chat_connection():
    """Test if chat server is accessible"""

    print("=" * 70)
    print("🔍 CHAT SERVER CONNECTION DIAGNOSTIC")
    print("=" * 70)

    # Get Railway URL from environment or use localhost
    railway_url = os.getenv('RAILWAY_WS_URL', 'ws://localhost:8766')

    print(f"\n1. Testing connection to: {railway_url}")
    print(f"   (Set RAILWAY_WS_URL env var to test production)")

    try:
        # Try to connect
        print("\n2. Attempting WebSocket connection...")
        async with websockets.connect(railway_url, ping_timeout=10) as websocket:
            print("   ✅ Connected successfully!")

            # Wait for welcome message
            print("\n3. Waiting for welcome message...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)
            print(f"   ✅ Received: {data}")

            # Send a test message
            print("\n4. Sending test message...")
            test_msg = {
                'type': 'user_message',
                'message': 'Hello Sarah! This is a connection test.'
            }
            await websocket.send(json.dumps(test_msg))
            print("   ✅ Message sent!")

            # Wait for Sarah's response
            print("\n5. Waiting for Sarah's response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            data = json.loads(response)
            print(f"   ✅ Sarah replied: {data.get('message', '')[:100]}...")

            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED - Chat server is working!")
            print("=" * 70)

    except asyncio.TimeoutError:
        print("\n❌ TIMEOUT - Server is not responding")
        print("\nPossible issues:")
        print("  - Chat server is not running")
        print("  - ANTHROPIC_API_KEY is missing")
        print("  - Network/firewall blocking connection")

    except ConnectionRefusedError:
        print("\n❌ CONNECTION REFUSED - Server is not listening")
        print("\nPossible issues:")
        print("  - Chat server hasn't started")
        print("  - Wrong port (should be 8766)")
        print("  - Railway deployment failed")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ INVALID STATUS CODE: {e}")
        print("\nPossible issues:")
        print("  - Server returned error status")
        print("  - Check Railway logs for errors")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        print("\nCheck Railway deployment logs for details")

    print("\n" + "=" * 70)
    print("💡 TROUBLESHOOTING STEPS:")
    print("=" * 70)
    print("\n1. Check Railway logs:")
    print("   - Go to Railway dashboard")
    print("   - Click on your deployment")
    print("   - Look for '💬 Chat server started' message")
    print("   - Check for any error messages")
    print("\n2. Verify environment variables in Railway:")
    print("   - ANTHROPIC_API_KEY should be set")
    print("   - Should start with 'sk-ant-'")
    print("\n3. Check Railway port exposure:")
    print("   - Railway should expose port 8766")
    print("   - Check Railway settings > Networking")
    print("\n4. Test locally first:")
    print("   - Run: python main.py")
    print("   - Then run: python test_chat_connection.py")
    print("   - If works locally, issue is with Railway")
    print("\n5. Rebuild Railway deployment:")
    print("   - Sometimes dependencies don't install correctly")
    print("   - Try: Settings > Redeploy")

if __name__ == "__main__":
    asyncio.run(test_chat_connection())
