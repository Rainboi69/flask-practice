\# Synchronous Request Timing Baseline



Endpoint: `/nutrition/eggs`



\- 1 call: 1.221 seconds

\- 3 sequential calls: 3.594 seconds

\- 5 sequential calls: 5.929 seconds



\*\*Observation:\*\* Total elapsed time grows roughly in proportion to the number of sequential requests because each request waits for the server response.

async_http.py — 3 sequential awaits to /nutrition/eggs

Command: py async_http.py
Total elapsed: 3.28 seconds
Date: 2026-11-01

async_http.py — 3 concurrent requests using asyncio.gather and httpx.AsyncClient

Command: py async_http.py
Total elapsed: 1.26 seconds
Date: 2026-11-01

Using a 2.0-second timeout for nutrition calls keeps the overall response fast, but we give up any nutrition results that would have arrived after 2 seconds.