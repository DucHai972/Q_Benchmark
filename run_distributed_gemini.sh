#!/bin/bash

# Distributed Gemini Benchmark Runner
# This script distributes 49 cases (2-50) across 11 Google API keys  
# 4 cases per key (keys 1-10), 9 cases for key 11
# Model: gemini-2.5-flash

echo "=== Gemini Benchmark Distribution ==="
echo "Total cases: 49 (starting from case 2), distributed across 11 Google API keys"
echo "Cases per key: 4 cases each (key 11 gets 9 cases)"
echo "Model: gemini-2.5-flash"
echo ""

echo "=== Final Case Distribution ==="
echo "Gemini 1  (reliable):     Cases 2-5   (4 cases)"
echo "Gemini 2  (z01):          Cases 6-9   (4 cases)"
echo "Gemini 3  (9722):         Cases 10-13 (4 cases)"
echo "Gemini 4  (sub01):        Cases 14-17 (4 cases)"
echo "Gemini 5  (sub02):        Cases 18-21 (4 cases)"
echo "Gemini 6  (sub03):        Cases 22-25 (4 cases)"
echo "Gemini 7  (qvt):          Cases 26-29 (4 cases)"
echo "Gemini 8  (sub04):        Cases 30-33 (4 cases)"
echo "Gemini 9  (sub05):        Cases 34-37 (4 cases)"
echo "Gemini 10 (geminisub01):  Cases 38-41 (4 cases)"
echo "Gemini 11 (geminisub03):  Cases 42-50 (9 cases)"
echo ""

echo "=== Ready-to-Run Scripts ==="
echo "All scripts use: set -a && source .env && set +a"
echo "Then export the specific GOOGLE_API_KEY for that script"
echo ""

echo "=== Usage Instructions ==="
echo "1. Create 11 screen sessions:"
echo "   screen -S gemini1, screen -S gemini2, ..., screen -S gemini11"
echo "2. In each screen, run the corresponding script:"
echo "   ./gemini1.sh, ./gemini2.sh, ..., ./gemini11.sh"
echo "3. Use 'screen -r geminiX' to reattach to any screen"
echo "4. Use Ctrl+A+D to detach from a screen"
echo ""
echo "Example:"
echo "screen -S gemini1"
echo "./gemini1.sh"
echo ""
echo "=== Parallel Running ==="
echo "You can run both OpenAI and Gemini simultaneously:"
echo "- 11 screens for OpenAI keys (key1.sh - key11.sh)"
echo "- 11 screens for Gemini keys (gemini1.sh - gemini11.sh)"
echo "- Total: 22 parallel benchmark processes!"
echo ""
echo "All Gemini scripts are ready to run!"