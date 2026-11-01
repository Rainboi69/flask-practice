import time


def cpu_work(iterations):
    total = 0

    for i in range(iterations):
        total += i

    return total


def main():
    iterations = 10_000_000

    start = time.perf_counter()
    result = cpu_work(iterations)
    end = time.perf_counter()

    print("Total:", result)
    print("Iterations:", iterations)
    print("Elapsed time:", round(end - start, 3), "seconds")


if __name__ == "__main__":
    main()