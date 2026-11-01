import os
import asyncio
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

NUTRITION_URL = os.getenv("NUTRITION_SERVICE_URL")
TIMEOUT_SECONDS = 2.0


async def fetch_eggs(client, endpoint):
    try:
        response = await asyncio.wait_for(
            client.get(f"{NUTRITION_URL}{endpoint}"),
            timeout=TIMEOUT_SECONDS,
        )

        return response.json()

    except TimeoutError:
        return {"status": "timeout", "data": None}


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [
           fetch_eggs(client, "/nutrition/eggs"),       # fast → should succeed
           fetch_eggs(client, "/nutrition/slow-eggs"),  # slow → should timeout
           fetch_eggs(client, "/nutrition/eggs"),       # fast → should succeed
        ]

        results = await asyncio.gather(*tasks)

        print("Results:", results)


if __name__ == "__main__":
    asyncio.run(main())