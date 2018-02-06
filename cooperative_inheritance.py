class A(object):
    def __init__(self, x):
        super().__init__()


class B(object):
    def __init__(self, x):
        super().__init__()


a = A(1)
b = B(2)


class C(A, B):
    def __init__(self, x):
        super().__init__(x)


# def extract_classname(repr):
#     repr = str(repr)
#     first = repr.find("'")
#     fullname = repr[first + 1:-2]
#     return fullname.split('.')[-1]
#
#
# # pprint(LoggingDict.__mro__)
# mro = " -> ".join([extract_classname(c) for c in C.__mro__])
# print(mro)


print(C.__mro__)
c = C(3)

