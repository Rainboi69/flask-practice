import threading
import time
import httpx

url = "http://127.0.0.1:5001/nutrition/eggs"


def make_request(number):
    response = httpx.get(url)
    print(f"Request {number}: {response.status_code}")


def main():
    threads = []

    start = time.perf_counter()

    for i in range(5):
        thread = threading.Thread(
            target=make_request,
            args=(i + 1,)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.perf_counter()

    print(
        "Total elapsed time for 5 threaded requests:",
        round(end - start, 3),
        "seconds"
    )


if __name__ == "__main__":
    main()