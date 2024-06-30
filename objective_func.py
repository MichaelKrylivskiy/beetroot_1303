import time
import requests
from threading import Thread
from multiprocessing import Process
import math


# Decorator for measuring execution time of functions
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result

    return wrapper


# Objective Functions (without the decorator)
def hello_world():
    for _ in range(100):
        print("Hello World")


def make_requests():
    for _ in range(100):
        response = requests.get("https://python.org")
        # Uncomment to see the response content
        # print(response.content[:100])


def read_folder_contents():
    import os
    for _ in range(100):
        for _ in os.listdir('.'):
            pass


def calculate_primes():
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                return False
        return True

    def find_primes(count):
        primes = []
        num = 2
        while len(primes) < count:
            if is_prime(num):
                primes.append(num)
            num += 1
        return primes

    find_primes(1001)


# Function executor for threads and processes
def execute_with_threads(func):
    threads = []
    for _ in range(5):
        thread = Thread(target=func)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def execute_with_processes(func):
    processes = []
    for _ in range(5):
        process = Process(target=func)
        processes.append(process)
        process.start()
        process.join()  # Wait for process to finish
    for process in processes:
        process.join()


# Main execution
if __name__ == "__main__":
    # Run each function in threads and processes
    for func in [hello_world, make_requests, read_folder_contents, calculate_primes]:
        print(f"\nExecuting {func.__name__} with threads:")
        execute_with_threads(func)

        print(f"\nExecuting {func.__name__} with processes:")
        execute_with_processes(func)
