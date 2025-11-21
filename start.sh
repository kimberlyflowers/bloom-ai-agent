#!/bin/bash
# Railway startup script for Sarah Rodriguez
# Sets up virtual display (Xvfb) and launches with REAL Chrome (not headless)

echo "🌸 Starting Sarah Rodriguez..."

# Install Playwright browsers (chromium only to save space)
echo "📦 Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

# START XVFB - Virtual Display for Real Chrome!
echo "🖥️  Starting Xvfb virtual display..."

# Create virtual display on :99 with 1920x1080 resolution, 24-bit color
Xvfb :99 -screen 0 1920x1080x24 -ac -nolisten tcp -dpi 96 +extension GLX +render -noreset &
XVFB_PID=$!

# Wait for Xvfb to start (give it 2 seconds)
sleep 2

# Verify Xvfb is running
if ps -p $XVFB_PID > /dev/null; then
    echo "✅ Xvfb started successfully on display :99 (PID: $XVFB_PID)"
else
    echo "❌ Xvfb failed to start!"
    exit 1
fi

# Set DISPLAY environment variable (tells Chrome to use virtual display)
export DISPLAY=:99

# Verify display is working
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ Virtual display :99 is ready!"
    echo "📺 Resolution: 1920x1080"
else
    echo "❌ Display :99 not responding!"
    exit 1
fi

# Start Sarah with REAL Chrome (not headless!)
echo "🚀 Launching Sarah with REAL Chrome on virtual display..."
echo "🎯 Browser fingerprint will look 100% authentic!"
python main.py

# Cleanup (kill Xvfb when app exits)
kill $XVFB_PID 2>/dev/null
