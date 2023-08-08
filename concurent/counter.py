import concurrent.futures
import multiprocessing as mp


def get_user_object(batch):
    with _COUNTER.get_lock():
        _COUNTER.value += 1
        print(_COUNTER.value, end=' ')


def init_globals(counter):
    global _COUNTER
    _COUNTER = counter


def main():
    counter = mp.Value('i', 0)
    with concurrent.futures.ProcessPoolExecutor(
        initializer=init_globals, initargs=(counter,)
    ) as executor:
        for _ in executor.map(get_user_object, range(10)):
            pass
    print()


if __name__ == "__main__":
    import sys
    sys.exit(main())