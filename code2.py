from typing import Any, Optional, Callable, Tuple
import threading
import queue
import heapq
import logging
import time

# Create loggers for both producer and consumer threads
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
producer_logger = logging.getLogger("ProducerThread")
consumer_logger = logging.getLogger("ConsumerThread")


class PriorityMessageQueue:
    """
    A thread-safe implementation of a priority queue.
    Messages can be enqueued with a priority and dequeued in the order of their priority.
    """

    def __init__(self) -> None:
        self.heap: list[Tuple[int, Any]] = []
        self.lock: threading.Lock = threading.Lock()
        self.condition: threading.Condition = threading.Condition(lock=self.lock)

    def enqueue(self, message: Tuple[int, Any]) -> None:
        """
        Enqueues a message with a priority.
        The message is added to the internal heap using the heapq.heappush() function.
        """
        with self.lock:
            heapq.heappush(self.heap, message)
            self.condition.notify()

    def dequeue(self) -> Tuple[int, Any]:
        """
        Dequeues and returns the message with the highest priority.
        If the queue is empty, the method waits until a message is available using the condition.wait() function.
        """
        with self.lock:
            while not self.heap:
                self.condition.wait()
            return heapq.heappop(self.heap)

    def peek(self) -> Optional[Tuple[int, Any]]:
        """
        Returns the message with the highest priority without removing it from the queue.
        If the queue is empty, it returns None.
        """
        with self.lock:
            return self.heap[0] if self.heap else None

    def is_empty(self) -> bool:
        """
        Returns True if the queue is empty, otherwise returns False.
        """
        with self.lock:
            return not bool(self.heap)

    def get_all_messages(self) -> list[Tuple[int, Any]]:
        """
        Returns a list of all messages in the queue.
        """
        with self.lock:
            return self.heap.copy()


class ThreadPool:
    """
    A class that manages a pool of worker threads and executes tasks concurrently.
    """

    def __init__(self, num_threads: int) -> None:
        """
        Initializes a ThreadPool object with the specified number of worker threads.

        Args:
            num_threads: The number of worker threads in the thread pool.
        """
        self.task_queue = queue.Queue()
        self.threads = [threading.Thread(target=self._worker) for _ in range(num_threads)]
        self.lock = threading.Lock()

    def start(self) -> None:
        """
        Starts the thread pool by starting all the worker threads.
        """
        for thread in self.threads:
            thread.start()

    def submit_task(self, task: Callable[[], None]) -> None:
        """
        Submits a task to the thread pool to be executed by one of the worker threads.

        Args:
            task: The task to be executed.
        """
        with self.lock:
            self.task_queue.put(task)
            self.task_queue.task_done()

    def _worker(self) -> None:
        """
        The internal worker function that runs in each worker thread.
        It continuously retrieves tasks from the task queue and executes them until a None task is encountered,
        indicating that the thread should exit.
        """
        while True:
            task = self.task_queue.get()
            if task is None:  # Signal to exit
                break
            task()

    def stop(self) -> None:
        """
        Stops the thread pool by adding None tasks to the task queue for each worker thread and joining all the worker threads.
        """
        with self.lock:
            for _ in self.threads:
                self.task_queue.put(None)
            for thread in self.threads:
                thread.join()


def send_message(sender: int, receiver: int, priority: int, content: Any) -> None:
    """
    Sends a message from one thread to another.

    Args:
        sender (int): The ID of the sending thread.
        receiver (int): The ID of the receiving thread.
        priority (int): The priority of the message.
        content (Any): The content of the message.

    Returns:
        None

    Raises:
        None
    """
    producer_logger.debug(f"Thread-{sender} sending message to Thread-{receiver} with priority {priority}: {content}")
    with message_queue_lock:
        message_queue[receiver].enqueue((priority, content))


def simple_action(message):
    print(f"Performing simple action: {message}")


def receiving_thread(thread_id):
    start_time = time.time()
    while True:
        consumer_logger.debug(f"Thread-{thread_id} checking for messages")
        if not message_queue[thread_id].is_empty():
            message = message_queue[thread_id].dequeue()
            thread_pool.submit_task(lambda: simple_action(message))
            start_time = time.time()  # Reset the start time
        else:
            # Sleep if the queue is empty
            time.sleep(3)
            if time.time() - start_time > 10:
                thread_pool.stop()  # Terminate the program
                break


# Initialize priority message queues for each thread
num_threads = 3  # int(input("Enter number of threads: "))
message_queue = [PriorityMessageQueue() for _ in range(num_threads)]
message_queue_lock = threading.Lock()

# Initialize thread pool
thread_pool = ThreadPool(num_threads=2)
thread_pool.start()

# Initialize receiving threads
receiving_threads = [threading.Thread(target=receiving_thread, args=(i,)) for i in range(num_threads)]
for thread in receiving_threads:
    thread.start()

# Test this implementation
time.sleep(1)
send_message(0, 1, 1, "Hello")
time.sleep(2)
send_message(1, 2, 2, "World")
time.sleep(3)
send_message(2, 0, 0, "Priority")
time.sleep(4)
send_message(0, 1, 0, "Queue")

# User Input to send messages
# def user_input():
#     sender_id = int(input("Enter sender ID: "))
#     receiver_id = int(input("Enter receiver ID: "))
#     priority = int(input("Enter priority: "))
#     message = input("Enter message: ")
#     send_message(sender_id, receiver_id, priority, message)

# time.sleep(1)
# choice = input("Do you want to send more messages? (y/n): ")
# if choice.lower() == "y":
#     while True:
#         user_input()
#         time.sleep(1)
#         choice = input("Do you want to send more messages? (y/n): ")
#         if choice.lower() != "y":
#             break

# Wait for threads to finish
for thread in receiving_threads:
    thread.join()

# Stop the thread pool
thread_pool.stop()