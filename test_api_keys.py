#!/usr/bin/env python3
import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_key(session, key_name, api_key):
    """Test a single OpenAI API key."""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Simple completion request to test the key
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }
        
        async with session.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=10) as response:
            if response.status == 200:
                return f"✅ {key_name}: WORKING"
            elif response.status == 401:
                return f"❌ {key_name}: INVALID (401 Unauthorized)"
            elif response.status == 429:
                return f"⚠️  {key_name}: RATE LIMITED (429)"
            elif response.status == 402:
                return f"💳 {key_name}: BILLING ISSUE (402)"
            else:
                result = await response.text()
                return f"❓ {key_name}: ERROR ({response.status}) - {result[:100]}"
                
    except asyncio.TimeoutError:
        return f"⏰ {key_name}: TIMEOUT"
    except Exception as e:
        return f"❌ {key_name}: ERROR - {str(e)[:100]}"

async def test_google_key(session, key_name, api_key):
    """Test a single Google API key."""
    try:
        # Test with Gemini API
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
        
        data = {
            "contents": [{
                "parts": [{"text": "Hello"}]
            }]
        }
        
        async with session.post(url, json=data, timeout=10) as response:
            if response.status == 200:
                return f"✅ {key_name}: WORKING"
            elif response.status == 401:
                return f"❌ {key_name}: INVALID (401 Unauthorized)"
            elif response.status == 403:
                return f"🚫 {key_name}: FORBIDDEN (403)"
            elif response.status == 429:
                return f"⚠️  {key_name}: RATE LIMITED (429)"
            else:
                result = await response.text()
                return f"❓ {key_name}: ERROR ({response.status}) - {result[:100]}"
                
    except asyncio.TimeoutError:
        return f"⏰ {key_name}: TIMEOUT"
    except Exception as e:
        return f"❌ {key_name}: ERROR - {str(e)[:100]}"

async def main():
    """Test all API keys."""
    print("🔍 Testing API Keys...\n")
    
    # Collect all API keys
    openai_keys = {}
    google_keys = {}
    
    for i in range(1, 12):  # 11 OpenAI keys
        key_name = f"OPENAI_API_KEY_{i}"
        api_key = os.getenv(key_name)
        if api_key:
            openai_keys[key_name] = api_key
    
    for i in range(1, 10):  # 9 Google keys
        key_name = f"GOOGLE_API_KEY_{i}"
        api_key = os.getenv(key_name)
        if api_key:
            google_keys[key_name] = api_key
    
    print(f"Found {len(openai_keys)} OpenAI keys and {len(google_keys)} Google keys\n")
    
    # Test all keys concurrently
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Add OpenAI key tests
        for key_name, api_key in openai_keys.items():
            tasks.append(test_openai_key(session, key_name, api_key))
        
        # Add Google key tests
        for key_name, api_key in google_keys.items():
            tasks.append(test_google_key(session, key_name, api_key))
        
        # Run all tests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Print results
        print("🤖 OPENAI API KEYS:")
        print("=" * 50)
        openai_working = 0
        openai_total = 0
        
        for result in results[:len(openai_keys)]:
            if isinstance(result, Exception):
                print(f"❌ ERROR: {result}")
            else:
                print(result)
                if "WORKING" in result:
                    openai_working += 1
                openai_total += 1
        
        print(f"\nOpenAI Summary: {openai_working}/{openai_total} working keys\n")
        
        print("🧠 GOOGLE API KEYS:")
        print("=" * 50)
        google_working = 0
        google_total = 0
        
        for result in results[len(openai_keys):]:
            if isinstance(result, Exception):
                print(f"❌ ERROR: {result}")
            else:
                print(result)
                if "WORKING" in result:
                    google_working += 1
                google_total += 1
        
        print(f"\nGoogle Summary: {google_working}/{google_total} working keys")
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"OpenAI: {openai_working}/{openai_total} working")
        print(f"Google: {google_working}/{google_total} working")
        print(f"Total: {openai_working + google_working}/{openai_total + google_total} working keys")

if __name__ == "__main__":
    asyncio.run(main())