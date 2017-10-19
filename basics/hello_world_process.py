import multiprocessing
import time


def worker():
    # The name of the process can be accessed.
    name = multiprocessing.current_process().name
    # And pid can be accessed.
    pid = multiprocessing.current_process().pid
    # We add some delay to mimic time-consuming work.
    time.sleep(0.1)

    print('Process %s(PID %d) says: Hello, world!' % (name, pid))


if __name__ == '__main__':
    # Define 10 processes and assign 'worker' function to each of the processes.
    processes = [multiprocessing.Process(target=worker, name=str(processId)) for processId in range(10)]
    # Make processes work. 
    for process in processes:
        process.start()
