#!/bin/bash
# Startup script for Railway - ensures Playwright browsers are installed

echo "🔧 Checking Playwright browser installation..."

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
