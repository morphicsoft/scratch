from functools import wraps


class Observable:

    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify(self, *args):
        result = all([obs.notify(*args) for obs in self._observers])
        if not result:
            raise RuntimeError("Failed event notification, args = {}".format(args))
        return result


class Thing(Observable):

    def __init__(self):
        Observable.__init__(self)


class Metaclass(type):

    _handlers = {}

    def __new__(typ, *args):
        klass = super(Metaclass, typ).__new__(typ, *args)
        if not klass.__name__ == 'Observer':
            klass._handlers = {k: v for k, v in Metaclass._handlers.items()}
            Metaclass._handlers = {}
        return klass

    # def __init__(cls):
    #     super(Metaclass, cls).__init__(cls)

    def foo(cls):
        pass


class Observer(metaclass=Metaclass):

    # __metaclass__ = Metaclass

    @classmethod
    def on(cls, *args):
        def wrap(f):
            Metaclass._handlers[args] = f

            @wraps(f)
            def wrapper(*args):
                return f(*args)

            return wrapper
        return wrap

    @classmethod
    def default(cls, f):
        Metaclass._handlers['__default__'] = f
        @wraps(f)
        def wrapper(*args):
            return f(*args)

        return wrapper

    def notify(self, *args):
        func = self._handlers.get(args) or self._handlers.get('__default__')
        if not func:
            raise NotImplementedError("No function match for {}".format(args))
        result = func(self)
        return result


class Manager(Observer):

    def __init__(self):
        Observer.__init__(self)

    @Observer.on('foo')
    def foo_handler(self):
        print("Manager received foo notification")
        return True

    @Observer.default
    def noop(self):
        print("Manager ignoring notification")
        return True


class Manager2(Observer):

    def __init__(self):
        Observer.__init__(self)

    @Observer.on('foo')
    @Observer.on('baz')
    def foo_handler(self):
        print("Manager2 received foo or baz notification")
        return True

    @Observer.on('bar')
    def bar_handler(self):
        print("Manager2 received bar notification")
        return True


if __name__ == '__main__':

    m = Manager()
    m2 = Manager2()

    t = Thing()
    t.add_observer(m)
    t.add_observer(m2)

    t.notify('foo')  # calls m->foo_handler
    t.notify('bar')
    t.notify('baz')
