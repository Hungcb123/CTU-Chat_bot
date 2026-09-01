#!/usr/bin/env python3
import os
import time
import requests
from dotenv import load_dotenv

# Load .env from current directory (we will run it from CTU-Chat_bot)
load_dotenv('.env')

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env")
    exit(1)

URL = "https://openrouter.ai/api/v1/embeddings"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://localhost",  # Required by OpenRouter
    "X-Title": "RateLimitTester"
}
MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
PAYLOAD = {
    "model": MODEL,
    "input": "Xin chào, đây là một câu test để kiểm tra tốc độ embedding."
}

def test_rate_limit():
    print(f"Testing rate limit for {MODEL} on OpenRouter...")
    print("Sending requests continuously. Stop with Ctrl+C.\n")
    
    start_time = time.time()
    success_count = 0
    
    while True:
        try:
            req_start = time.time()
            response = requests.post(URL, headers=HEADERS, json=PAYLOAD)
            req_time = time.time() - req_start
            
            if response.status_code == 200:
                data = response.json()
                # On the first success, let's print the dimension size
                if success_count == 0:
                    try:
                        vector = data['data'][0]['embedding']
                        print(f"✅ Success! Vector dimension size: {len(vector)}")
                    except (KeyError, IndexError):
                        print("Could not parse vector dimension from response:", data)
                        
                success_count += 1
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] Request {success_count} OK ({req_time:.2f}s)")
                
                # If we've reached 100 requests
                if success_count >= 100:
                    print(f"\n🎉 Test finished! Successfully made {success_count} requests in {elapsed:.1f} seconds.")
                    break
                    
            elif response.status_code == 429:
                elapsed = time.time() - start_time
                print(f"\n❌ RATE LIMIT HIT! Got 429 Too Many Requests.")
                print(f"Made {success_count} successful requests in {elapsed:.1f} seconds before getting blocked.")
                print("Response:", response.text)
                break
            else:
                print(f"\n⚠️ Unexpected status code: {response.status_code}")
                print("Response:", response.text)
                break
                
        except Exception as e:
            print(f"\n❌ Error during request: {e}")
            break

if __name__ == "__main__":
    test_rate_limit()
