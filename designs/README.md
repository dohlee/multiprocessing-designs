# Designs

It is often a bother to implement multithreaded programs in python. Here are some example implementations of multithreaded-programming designs in python. 

## Producer-Consumer problem

In producer-consumer problem, each thread works as either *producer* or *consumer*. *Producer* produces tasks which should be processed by *consumer*. Several points should be considered when implementing producer-consumer problem.

- **Tasks and status of tasks should be shared between producers and consumers.**

  This can be done by defining `WorkManager` class which has `multiprocessing.Queue` objects as a class variable. As producers and consumers are spawned by the process which generated `WorkManager` object, producers and consumers are free to access those queues. 

- **Consumers should wait until tasks are available (i.e. producer produces tasks).**

  As `multiprocessing.Queue` object is implemented to be thread-safe, consumer processes automatically block after calling `multiprocessing.Queue.get` method until the queue is not empty.

- **When all tasks are processed, consumer threads should be automatically killed.**

  This can be accomplished by putting *poison pills* to task queue if all tasks are produced. When a consumer gets a *poison pill* from task queue, it can be sure that there isn't any remaining tasks in the queue, thus it immediately kills itself.



### Single producer-Multiple consumer problem



