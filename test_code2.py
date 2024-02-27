import time

def task1():
    print("Executing task 1...")
    time.sleep(1)
    print("Task 1 executed.")

def task2():
    print("Executing task 2...")
    time.sleep(2)
    print("Task 2 executed.")

def task3():
    print("Executing task 3...")
    time.sleep(0.5)
    print("Task 3 executed.")

def test_thread_pool():
    # Create a thread pool with 2 worker threads
    thread_pool = ThreadPool(2)

    # Start the thread pool
    thread_pool.start()

    # Submit tasks to the thread pool
    thread_pool.submit_task(task1)
    thread_pool.submit_task(task2)
    thread_pool.submit_task(task3)

    # Wait for all tasks to complete
    time.sleep(3)

    # Stop the thread pool
    thread_pool.stop()

# Run the test
test_thread_pool()