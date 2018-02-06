

class classproperty(object):

    def __init__(self, fget=None):
        self._fget = fget

    # def __getattribute__(self, propname):
    #     print("classproperty.__getattribute__({})".format(propname))

    def __get__(self, _, klass):
        return self._fget(klass)


class C:

    FOO = 'bar'

    def __init__(self):
        pass

    @classproperty
    def x(klass):
        return klass.FOO

    @classmethod
    def f(klass):
        return klass.x


if __name__ == '__main__':

    print(C.f())
