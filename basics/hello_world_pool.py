import multiprocessing
import time


def worker(name):
    # pid can be accessed.
    pid = multiprocessing.current_process().pid
    # We add some delay to mimic time-consuming work.
    time.sleep(0.1)

    return 'Process %s(PID %d) says: Hello, world!' % (name, pid)


if __name__ == '__main__':
    # Define a process pool with 5 processes.
    pool = multiprocessing.Pool(processes=5)
    # Assign ten jobs to the processes and collect their results.
    results = pool.map(worker, range(10))
    # Print each of the results.
    for result in results:
        print(result)
    
