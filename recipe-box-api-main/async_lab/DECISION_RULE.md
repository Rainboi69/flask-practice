\# DRAFT: Execution Model Decision Rule

\*Will be revised after async measurements.\*



\## When to use synchronous code

I would use basic synchronous code when a program only needs to make a few quick requests or perform simple tasks. Synchronous code is easier to write, read, and troubleshoot because each step happens one after another. If the workload is small and performance is already good, there may be no need to add the extra complexity of threads or asynchronous programming.



## When to use threads for blocking I/O

I would use threads for I/O-bound tasks, such as making multiple HTTP requests or working with files and networks. Threads are useful when several independent tasks spend most of their time waiting because they allow those waiting periods to overlap. They can improve performance without having to rewrite the whole program using async, although they do add some complexity.



## When to use async

I would use async with `httpx.AsyncClient` and `asyncio.gather` when a program needs to make multiple independent I/O-bound HTTP requests concurrently. This allows requests to overlap while waiting for responses instead of waiting for each request to finish before starting the next.

In my slow nutrition service experiment, 3 sequential async requests took about 3.28 seconds, while 3 concurrent requests using `asyncio.gather` took about 1.26 seconds — roughly the time of one request.

This measurement applies to my specific test workload and does not mean every async workload will perform this way. Async is especially useful when there are many I/O-bound operations that can overlap.



\## When to use processes for CPU-bound work

For CPU-heavy Python tasks, threads may not improve performance because of the Global Interpreter Lock (GIL). I would consider using multiple processes with tools such as Python's `multiprocessing` module to run calculations across multiple CPU cores. Implementing processes is outside the scope of this lesson, but it is the direction I would investigate for CPU-bound work.
