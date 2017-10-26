import multiprocessing
import time
import random


class Producer(multiprocessing.Process):
    def __init__(self, taskQueue, ingredients, numConsumers):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.ingredients = ingredients
        self.numConsumers = numConsumers

    def run(self):
        # Do some work with ingredients and enqueue tasks from here
        for task in self.tasks():
            self.taskQueue.put(task)
            print("[Producer %d] Produced task %d" % (self.pid, task))
        # to here.

        # At last, put poison pills to stop consumers working.
        for _ in range(self.numConsumers):
            self.taskQueue.put(None)

        print("[Producer %d] ===== Produced all tasks. =====" % self.pid)

    def tasks(self):
        """Generate task from ingredients."""
        for ingredient in self.ingredients:
            # Pretend to take some time to generate task.
            time.sleep(random.random() * 0.5)
            yield 2 * ingredient


class Consumer(multiprocessing.Process):
    def __init__(self, taskQueue, resultQueue, aliveConsumerQueue):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue

    def process_task(self, task, result):
        return result + task ** 2

    def run(self):
        # Accumulate square of each task.
        result = 0

        while True:
            task = self.taskQueue.get()

            # If consumer has met poison pill, stop working.
            if task is None:
                self.taskQueue.task_done()
                self.resultQueue.put(result)
                self.aliveConsumerQueue.get()
                print(' ' * 35 + "[Consumer %d] Consumed poison pill. Terminating..." % self.pid)
                break

            # Do some work from here
            time.sleep(random.random() * 2)  # Pretend to take some time to process task.
            result = self.process_task(task, result)
            self.taskQueue.task_done()  # Indicate the task is done so that taskQueue.join() does not block.
            print(' ' * 35 + "[Consumer %d] Processed task %d." % (self.pid, task))
            # to here.
    
class Tracer(multiprocessing.Process):
    def __init__(self, taskQueue, resultQueue, aliveConsumerQueue, interval=1):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue
        self.aliveConsumerQueue = aliveConsumerQueue

        self.interval = interval

    def run(self):
        while True:
            time.sleep(self.interval)

            if self.aliveConsumerQueue.qsize() == 0:
                break

class WorkManager:
    def __init__(self, ingredients, numConsumers):
        self.taskQueue = multiprocessing.JoinableQueue()
        self.resultQueue = multiprocessing.JoinableQueue()
        self.aliveConsumerQueue = multiprocessing.JoinableQueue()
        for _ in range(numConsumers):
            self.aliveConsumerQueue.put(None)

        self.producer = Producer(self.taskQueue, ingredients, numConsumers=numConsumers)
        self.consumers = [Consumer(self.taskQueue, self.resultQueue, self.aliveConsumerQueue) for _ in range(numConsumers)]
        self.tracer = Tracer(self.taskQueue, self.resultQueue)

    def start(self):
        self.producer.start()

        for consumer in self.consumers:
            consumer.start()

        self.taskQueue.join()
        self.resultQueue.join()
        self.taskQueue.close()
        self.resultQueue.close()

        self.producer.join()
        for consumer in self.consumers:
            consumer.join()

    def get_result(self):
        result = 0

        for _ in range(len(self.consumers)):
            result += self.resultQueue.get()
            self.resultQueue.taskQueue()

        return result

if __name__ == '__main__':
    ingredients = range(500)

    manager = WorkManager(ingredients, numConsumers=2)
    manager.start()