

class PropDict:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                self.__dict__[k] = PropDict(**v)
            else:
                self.__dict__[k] = v


if __name__ == '__main__':

    d = {
        'a': 1,
        'b': 2,
        'c': {
            'd': 5
        }
    }

    pd = PropDict(**d)
    print(pd.a)
    print(pd.b)
    print(pd.c)
    print(pd.c.d)
