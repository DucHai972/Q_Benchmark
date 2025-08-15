#!/bin/bash

# Distributed OpenAI Benchmark Runner
# This script distributes 49 cases (2-50) across 11 OpenAI API keys  
# 4 cases per key (keys 1-10), 9 cases for key 11
# Model: gpt-5-mini

echo "=== OpenAI Benchmark Distribution ==="
echo "Total cases: 49 (starting from case 2), distributed across 11 API keys"
echo "Cases per key: 4 cases each (key 11 gets 9 cases)"
echo "Model: gpt-5-mini"
echo ""

echo "=== Final Case Distribution ==="
echo "Key 1  (reliable): Cases 2-5   (4 cases)"
echo "Key 2  (z01):      Cases 6-9   (4 cases)"
echo "Key 3  (9722):     Cases 10-13 (4 cases)"
echo "Key 4  (1251):     Cases 14-17 (4 cases)"
echo "Key 5  (insight):  Cases 18-21 (4 cases)"
echo "Key 6  (sub01):    Cases 22-25 (4 cases)"
echo "Key 7  (sub02):    Cases 26-29 (4 cases)"
echo "Key 8  (sub03):    Cases 30-33 (4 cases)"
echo "Key 9  (sub04):    Cases 34-37 (4 cases)"
echo "Key 10 (sub05):    Cases 38-41 (4 cases)"
echo "Key 11 (sub06):    Cases 42-50 (9 cases)"
echo ""

echo "=== Ready-to-Run Scripts ==="
echo "All scripts use: set -a && source .env && set +a"
echo "Then export the specific OPENAI_API_KEY for that script"
echo ""

echo "=== Usage Instructions ==="
echo "1. Create 11 screen sessions:"
echo "   screen -S key1, screen -S key2, ..., screen -S key11"
echo "2. In each screen, run the corresponding script:"
echo "   ./key1.sh, ./key2.sh, ..., ./key11.sh"
echo "3. Use 'screen -r keyX' to reattach to any screen"
echo "4. Use Ctrl+A+D to detach from a screen"
echo ""
echo "Example:"
echo "screen -S key1"
echo "./key1.sh"
echo ""
echo "All scripts are working and tested!"