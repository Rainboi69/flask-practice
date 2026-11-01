import threading
import time


def cpu_work(iterations):
    total = 0

    for i in range(iterations):
        total += i

    return total


def main():
    total_iterations = 10_000_000
    number_of_threads = 4
    iterations_per_thread = total_iterations // number_of_threads

    threads = []

    start = time.perf_counter()

    for _ in range(number_of_threads):
        thread = threading.Thread(
            target=cpu_work,
            args=(iterations_per_thread,)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.perf_counter()

    print("Threads:", number_of_threads)
    print("Total iterations:", total_iterations)
    print("Elapsed time:", round(end - start, 3), "seconds")


if __name__ == "__main__":
    main()