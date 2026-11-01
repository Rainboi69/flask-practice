import asyncio
import httpx
import time


async def fetch_eggs(client):
    response = await client.get(
        "http://127.0.0.1:5001/nutrition/eggs"
    )
    print("Got one:", response.status_code)
    return response.json()


async def main():
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_eggs(client),
            fetch_eggs(client),
            fetch_eggs(client),
        ]

        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    print("Results:", results)
    print("Total elapsed:", elapsed, "seconds")


if __name__ == "__main__":
    asyncio.run(main())