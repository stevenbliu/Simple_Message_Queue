import threading
import queue
import random
import time

# Create a shared queue for both consumers
shared_queue = queue.Queue()  # Queue is thread-safe built-in.

# Global counter and lock
total_count = 0
producer_count = 0

lock = threading.Lock()

# Flag to signal when all publishers are done
all_publishers_done = threading.Event()

# Flag for controlling sleep
enable_sleep = False
# enable_sleep=True
print(f'time.sleep {enable_sleep}')

# Track how many publishers are done
publishers_done_count = 0
publishers_done_lock = threading.Lock()  # Lock to safely update the count

class Publisher:
    def __init__(self, shared_queue, num_messages, name):
        self.shared_queue = shared_queue
        self.num_messages = num_messages
        self.name = name

    def produce(self):
        """Produce random numbers and add them to the shared queue"""
        global producer_count

        for i in range(self.num_messages):
            num = random.randint(1, 100)
            print(f"{self.name} Adding item #{producer_count} - {num} to the queue")
            with lock:
                producer_count += 1

            self.shared_queue.put(num)  # Push to the shared queue
            
            if enable_sleep:
                time.sleep(0.0001)

        # Increment the publisher done count when the publisher finishes
        global publishers_done_count
        with publishers_done_lock:
            publishers_done_count += 1
            print(f"{self.name} finished producing. {publishers_done_count} out of {NUM_PUBLISHERS} publishers done.")

        # Set the event and add sentinel values when all publishers are done
        if publishers_done_count == NUM_PUBLISHERS:
            # all_publishers_done.set()
            print("All publishers are done. Adding sentinel values.")
            for _ in range(NUM_CONSUMERS):
                self.shared_queue.put(None)  # Add one sentinel per consumer

class Consumer:
    def __init__(self, shared_queue, name, count_type):
        self.shared_queue = shared_queue
        self.name = name
        self.count_type = count_type  # Even or Odd count
        self.local_count = 0  # To keep track of each consumer's count

    def count(self):
        """Consume from the shared queue and count the numbers"""
        global total_count  # Access the global counter
        print(f"{self.name} started processing.")
        
        while True:
            num = self.shared_queue.get()  # Get a message from the queue

            if num is None:  # Exit if sentinel value is received
                print(f"{self.name} received sentinel value. Exiting.")
                self.shared_queue.task_done()
                break

            print(f"{self.name} received {num} - Item #{total_count}")

            if (self.count_type == "even" and num % 2 == 0) or (self.count_type == "odd" and num % 2 != 0):
                self.local_count += 1

            # Safely update the global total_count
            with lock:
                total_count += 1

            self.shared_queue.task_done()  # Mark task as done

# Number of messages each publisher will produce
NUM_MESSAGES = 500

# Number of publishers and consumers
NUM_PUBLISHERS = 2  # Set how many publishers you want
NUM_CONSUMERS = 2  # Set how many consumers you want

# Create and start publisher threads dynamically
publishers = []
for i in range(NUM_PUBLISHERS):
    publisher_name = f"Publisher_{i+1}"
    publisher = Publisher(shared_queue, NUM_MESSAGES, publisher_name)
    pub_thread = threading.Thread(target=publisher.produce)
    publishers.append(pub_thread)
    pub_thread.start()

# Create and start consumer threads dynamically
consumers = []
for i in range(NUM_CONSUMERS):
    consumer_name = f"Consumer_{i+1}"
    count_type = "even" if i % 2 == 0 else "odd"  # Alternate between even and odd consumers
    consumer = Consumer(shared_queue, consumer_name, count_type)
    consumer_thread = threading.Thread(target=consumer.count)
    consumers.append(consumer_thread)
    consumer_thread.start()

# Debug: Monitor the queue size in each cycle (reduced printing frequency)
def monitor_queue():
    time.sleep(1)  # Give it a second before checking
    print(f"Starting queue size: {shared_queue.qsize()}")
    while not shared_queue.empty():
        time.sleep(1)  # Check every second
    print(f"Queue size after processing: {shared_queue.qsize()}")

# Start monitoring the queue
monitor_thread = threading.Thread(target=monitor_queue)
monitor_thread.daemon = True
monitor_thread.start()

# Wait for all publisher threads to finish
for pub_thread in publishers:
    pub_thread.join()

# Wait for all consumer threads to finish
for consumer_thread in consumers:
    consumer_thread.join()

print(f"Processing complete. Total counted: {total_count}. Exiting.")
