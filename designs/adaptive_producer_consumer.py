import multiprocessing
import time
import random
import queue

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
    def __init__(self, taskQueue, resultQueue, poisonPillQueue):
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue
        self.poisonPillQueue = poisonPillQueue

    def run(self):
        while True:
            try:
                poisonPill = self.poisonPillQueue.get(block=False)
                if poisonPill is None:
                    print(' ' * 35 + "[Consumer %d] Consumed poison pill. Terminating..." % self.pid)
                    self.poisonPillQueue.task_done()
                    break

            except queue.Empty:
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

class AdaptiveWorkManager:
    def __init__(self, ingredients, numProducers, numConsumers, maxTasks, maxConsumers, interval=1):
        self.taskQueue = multiprocessing.JoinableQueue()
        self.ingredientQueue = self.enqueue_ingredients(ingredients, numProducers)
        self.resultQueue = multiprocessing.JoinableQueue()
        self.poisonPillQueue = multiprocessing.JoinableQueue()
        self.producers = [Producer(self.taskQueue, self.ingredientQueue, numConsumers=numConsumers) for _ in range(numProducers)]
        self.consumers = [Consumer(self.taskQueue, self.resultQueue, self.poisonPillQueue) for _ in range(numConsumers)]
        self.maxConsumers = maxConsumers
        self.maxTasks = maxTasks
        self.interval = interval
        # self.arbiter = Arbiter(self.producers, self.consumers, self.taskQueue, self.resultQueue, self.poisonPillQueue, maxTasks=maxTasks, maxConsumers=maxConsumers, interval=interval)

    def enqueue_ingredients(self, ingredients, numProducers):
        ingredientQueue = multiprocessing.JoinableQueue()
        for ingredient in ingredients:
            ingredientQueue.put(ingredient)

        for _ in range(numProducers):
            ingredientQueue.put(None)

        return ingredientQueue

    def start(self):
        self.start_all_()
        self.monitor_()
        self.join_all_()

    def monitor_(self):
        while True:
            time.sleep(self.interval)

            aliveConsumerCount = sum(consumer.is_alive() for consumer in self.consumers)
            aliveProducerCount = sum(producer.is_alive() for producer in self.producers)
            print(' ' * 70 + '[AdaptiveWorkManager] Total [%d alive / %d] consumers and %d tasks are there.' % (aliveConsumerCount, len(self.consumers), self.taskQueue.qsize()))

            

            if self.taskQueue.qsize() > self.maxTasks and len(self.consumers) < self.maxConsumers:
                newConsumer = Consumer(self.taskQueue, self.resultQueue, self.poisonPillQueue)
                self.consumers.append(newConsumer)
                newConsumer.start()
                print(' ' * 70 + '[AdaptiveWorkManager] Adding new consumer')

            elif self.taskQueue.qsize() == 0:
                if aliveProducerCount == 0:
                    for _ in range(aliveConsumerCount):
                        self.taskQueue.put(None)
                    break

                self.taskQueue.put(None)
                print(' ' * 70 + '[AdaptiveWorkManager] Killing a consumer.')

    def start_all_(self):
        for producer in self.producers:
            producer.start()

        for consumer in self.consumers:
            consumer.start()

    def join_all_(self):
        self.taskQueue.join()
        self.resultQueue.join()
        self.ingredientQueue.join()
        self.poisonPillQueue.join()
        self.taskQueue.close()
        self.resultQueue.close()
        self.ingredientQueue.close()
        self.poisonPillQueue.close()

        for producer in self.producers:
            producer.join()
        for consumer in self.consumers:
            consumer.join()


if __name__ == '__main__':
    ingredients = range(100)

    manager = AdaptiveWorkManager(ingredients, numProducers=3, numConsumers=1, maxTasks=20, maxConsumers=20, interval=0.1)
    manager.start()