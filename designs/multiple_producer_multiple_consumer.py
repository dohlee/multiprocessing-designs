import multiprocessing
import time
import random


class Producer(multiprocessing.Process):
    def __init__(self, taskQueue, ingredientQueue, numConsumers):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.ingredientQueue = ingredientQueue
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
        while True:
            ingredient = self.ingredientQueue.get()
            # If poison pill appears, stop generating tasks.
            if ingredient is None:
                self.ingredientQueue.task_done()
                raise StopIteration

            # Pretend to take some time to generate task.
            time.sleep(random.random() * 0.5)
            self.ingredientQueue.task_done()
            yield 2 * ingredient


class Consumer(multiprocessing.Process):
    def __init__(self, taskQueue, resultQueue):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue

    def run(self):
        while True:
            task = self.taskQueue.get()

            # If consumer has met poison pill, stop working.
            if task is None:
                self.taskQueue.task_done()
                print(' ' * 35 + "[Consumer %d] Consumed poison pill. Terminating..." % self.pid)
                break

            # Do some work from here
            time.sleep(random.random() * 2)  # Pretend to take some time to process task.
            self.taskQueue.task_done()  # Indicate the task is done so that taskQueue.join() does not block.
            print(' ' * 35 + "[Consumer %d] Processed task %d." % (self.pid, task))
            # to here.
    
        
class WorkManager:
    def __init__(self, ingredients, numProducers, numConsumers):
        self.taskQueue = multiprocessing.JoinableQueue()
        self.ingredientQueue = self.enqueue_ingredients(ingredients, numProducers)
        self.resultQueue = multiprocessing.JoinableQueue()
        self.producers = [Producer(self.taskQueue, self.ingredientQueue, numConsumers=numConsumers) for _ in range(numProducers)]
        self.consumers = [Consumer(self.taskQueue, self.resultQueue) for _ in range(numConsumers)]

    def enqueue_ingredients(self, ingredients, numProducers):
        ingredientQueue = multiprocessing.JoinableQueue()
        for ingredient in ingredients:
            ingredientQueue.put(ingredient)

        for _ in range(numProducers):
            ingredientQueue.put(None)

        return ingredientQueue

    def start(self):
        for producer in self.producers:
            producer.start()

        for consumer in self.consumers:
            consumer.start()

        self.taskQueue.join()
        self.resultQueue.join()
        self.ingredientQueue.join()
        self.taskQueue.close()
        self.resultQueue.close()
        self.ingredientQueue.close()


        for producer in self.producers:
            producer.join()
        for consumer in self.consumers:
            consumer.join()


if __name__ == '__main__':
    ingredients = range(100)

    manager = WorkManager(ingredients, numProducers=4, numConsumers=2)
    manager.start()