#!/bin/bash
# Startup script for Railway - ensures Playwright browsers are installed

echo "🔧 Checking for available browsers..."

# Search for Chrome/Chromium executables
echo "📍 Searching for system browsers..."
find /usr -name "*chrome*" 2>/dev/null | head -10
find /usr -name "v*" -type f -executable 2>/dev/null | grep -i chrome | head -10

# List common browser locations
for browser in /usr/bin/google-chrome /usr/bin/chromium /usr/bin/chromium-browser /usr/bin/chrome; do
    if [ -f "$browser" ]; then
        echo "✅ Found: $browser"
    fi
done

# Check if chromium is already installed
if [ ! -d "/root/.cache/ms-playwright/chromium_headless_shell-1194" ]; then
    echo "📦 Installing Playwright browsers..."
    playwright install --with-deps chromium
    echo "✅ Playwright browsers installed!"
else
    echo "✅ Playwright browsers already installed"
fi

echo "🚀 Starting Sarah..."
python main.py
