import threading
import queue
import random
import time

class Publisher:
    def __init__(self, shared_queue, num_messages, name):
        self.shared_queue = shared_queue
        self.num_messages = num_messages
        self.name = name

    def produce(self):
        """Produce random numbers and add them to the shared queue"""
        for _ in range(self.num_messages):
            num = random.randint(1, 100)
            print(f"{self.name} produced: {num}")
            self.shared_queue.put(num)  # Push to the shared queue
            time.sleep(0.5)

        # Add sentinel values for each consumer
        self.shared_queue.put(None)  
        self.shared_queue.put(None)  

class Consumer:
    def __init__(self, shared_queue, name, count_type):
        self.shared_queue = shared_queue
        self.name = name
        self.count_type = count_type  # Even or Odd count

    def count(self):
        """Consume from the shared queue and count the numbers"""
        count = 0
        while True:
            print(f"{self.name} started counting {self.count_type}")

            num = self.shared_queue.get()
            if num is None:  # Sentinel value, exit the loop
                break
            
            if (self.count_type == "even" and num % 2 == 0) or (self.count_type == "odd" and num % 2 != 0):
                count += 1
                print(f"{self.name} counted {self.count_type}: {num}")
            else:
                print(f"{self.name} skipped {self.count_type}: {num}")
            self.shared_queue.task_done()  # Mark task as done

# Create a shared queue for both consumers
shared_queue = queue.Queue()

# Number of messages the publisher will produce
NUM_MESSAGES = 10

# Instantiate the Publisher
publisher = Publisher(shared_queue, NUM_MESSAGES, 'Pub1')
publisher2 = Publisher(shared_queue, NUM_MESSAGES, 'Pub2')

# Instantiate Consumers for even and odd counting
consumer_even = Consumer(shared_queue, "Consumer1", "even")
consumer_odd = Consumer(shared_queue, "Consumer2", "odd")

# Create threads for publisher and consumers
pub_thread = threading.Thread(target=publisher.produce)
pub_thread2 = threading.Thread(target=publisher2.produce)

consumer_even_thread = threading.Thread(target=consumer_even.count)
consumer_odd_thread = threading.Thread(target=consumer_odd.count)

# Start all threads
pub_thread.start()
pub_thread2.start()
consumer_even_thread.start()
consumer_odd_thread.start()

# Wait for threads to finish
pub_thread.join()
pub_thread2.join()
consumer_even_thread.join()
consumer_odd_thread.join()

print("Processing complete. Exiting.")
