import asyncio
import httpx
from pathlib import Path

async def main():
    api_key = "llx-UPOmlt8qMiAxlyVJaiI0Sq4joeQHXuGRplrZwXbDHjqBqJjT"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Create a dummy pdf or txt file
    dummy_file = Path("dummy.txt")
    dummy_file.write_text("Hello World!")
    
    async with httpx.AsyncClient(headers=headers, timeout=60) as client:
        # Upload
        with open(dummy_file, "rb") as f:
            files = {"file": (dummy_file.name, f, "text/plain")}
            resp = await client.post("https://api.cloud.llamaindex.ai/api/parsing/upload", files=files)
            print("Upload:", resp.json())
            job_id = resp.json()["id"]
            
        # Wait
        while True:
            resp = await client.get(f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}")
            status = resp.json()["status"]
            print("Status:", status)
            if status == "SUCCESS": break
            await asyncio.sleep(2)
            
        # Get JSON
        resp = await client.get(f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/json")
        print("JSON Result:", str(resp.json())[:500])

if __name__ == "__main__":
    asyncio.run(main())
