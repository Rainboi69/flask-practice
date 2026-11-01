import asyncio
import time

async def task_a():
    await asyncio.sleep(1)
    print("A done")

async def task_b():
    await asyncio.sleep(2)
    print("B done")

async def task_c():
    await asyncio.sleep(3)
    print("C done")


async def main():
    start = time.perf_counter()

    await task_a()
    await task_b()
    await task_c()

    end = time.perf_counter()

    print(f"sequential total: {end - start:.2f} seconds")


async def main_concurrent():
    task1 = asyncio.create_task(long_sleep())
    task2 = asyncio.create_task(medium_sleep())
    task3 = asyncio.create_task(short_sleep())

    results = await asyncio.gather(task1, task2, task3)

    print("results from gather:", results)


async def long_sleep():
    await asyncio.sleep(3)
    print("long done")
    return "long_result"


async def medium_sleep():
    await asyncio.sleep(2)
    print("medium done")
    return "medium_result"


async def short_sleep():
    await asyncio.sleep(1)
    print("short done")
    return "short_result"


asyncio.run(main())
asyncio.run(main_concurrent())