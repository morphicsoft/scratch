import collections
from pprint import pprint


class LoggingDict(dict):
    def __setitem__(self, key, value):
        print('Setting to %r' % (key, value))
        super().__setitem__(key, value)


class LoggingOD(LoggingDict, collections.OrderedDict):
    pass


"""
MRO is calculated (mostly) as:
 1. depth-first left-to-right order.
 2. where duplicates exist, all but the right-most duplicate is removed 

Thus the expected MRO for LoggingOD would be:
 1. LoggingOD -> LoggingDict -> dict -> object -> OrderedDict -> dict -> object

Removing left-most duplicates results in:
 2. LoggingOD -> LoggingDict -> OrderedDict -> dict -> object
"""


def extract_classname(repr):
    repr = str(repr)
    first = repr.find("'")
    fullname = repr[first + 1:-2]
    return fullname.split('.')[-1]


# pprint(LoggingDict.__mro__)
mro = " -> ".join([extract_classname(c) for c in LoggingOD.__mro__])
print(mro)


class A(object):
    def __init__(self, x):
        super(A, self).__init__()


class B(object):
    def __init__(self, x):
        super(B, self).__init__()


class C(A, B):
    def __init__(self, x):
        super(C, self).__init__(x)


a = A(5)
print(a)

b = B(10)
print(b)

c = C(15)
print(c)
