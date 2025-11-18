#!/bin/bash

echo "=================================="
echo "AI Multi-Agent System - Installation"
echo "=================================="
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "Note: Some features may require sudo privileges"
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "Creating necessary directories..."
mkdir -p /srv/ai_system/logs
mkdir -p /srv/ai_system/backups
mkdir -p /srv/ai_system/configs

echo "✓ Directories created"

echo ""
echo "=================================="
echo "Installation completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit configs/config.yaml with your settings"
echo "2. Run: python main.py start"
echo ""
