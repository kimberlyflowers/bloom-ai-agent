#!/bin/bash
# Railway startup script for Sarah Rodriguez
# Installs Playwright browsers and starts the application

echo "🌸 Starting Sarah Rodriguez..."

# Install Playwright browsers (chromium only to save space)
echo "📦 Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

# Start Sarah
echo "🚀 Launching Sarah..."
python main.py
