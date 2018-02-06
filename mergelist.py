import functools
import operator

list1 = [1, 2]
list2 = [1, 3, 5, 7, 9]
list3 = [1, 2, 3, 4]
list4 = [7, 2, 4]


def mergelist(*args):
    return functools.reduce(operator.add, args) if args else []


print(mergelist(list2, list3, list4))
