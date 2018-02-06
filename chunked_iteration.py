import itertools
import random


def rand_size():
    return random.randint(3,9)


def batch_iter(iterable, size):
    """
    Enables iteration over an iterable in batches of specified size. E.g.

    >>> def number_generator():
    >>>    for i in range(10):
    >>>        yield i
    >>> for batch in batch_iter(number_generator(), 3):
    >>>    print(list(batch))
    [0, 1, 2]
    [3, 4, 5]
    [6, 7, 8]
    [9]

    :param iterable: An iterable item, such as a sequence or generator object.
    :param size: The desired batch size.
    """
    source_iter = iter(iterable)
    while True:
        batchiter = itertools.islice(source_iter, size)
        yield itertools.chain([next(batchiter)], batchiter)


def dynamic_batch_iter(iterable, size_func):
    """
    The same as `batch_iter` but allows for a dynamic batch sizing using a callable to return the size.

    :param iterable: An iterable item, such as a sequence or generator object.
    :param size_func: A function which returns an integer to be used as the batch size.
    """
    source_iter = iter(iterable)
    while True:
        batchiter = itertools.islice(source_iter, size_func())
        yield itertools.chain([next(batchiter)], batchiter)


if __name__ == '__main__':
    def number_generator():
        for i in range(100):
            yield i

    for batch in dynamic_batch_iter(number_generator(), rand_size):
        print(list(batch))
