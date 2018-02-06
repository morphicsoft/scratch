import re

RegexType = type(re.compile(''))


class Demultiplexer:
    def __init__(self):
        self._route_handlers = []

    def add_route_handler(self, handler, **route):
        self._route_handlers.append((handler, route))

    def write(self, **kwargs):
        for handler in self._match_route(**kwargs):
            handler.write(**kwargs)

    def _match_route(self, **kwargs):
        return (
            handler for handler, route in self._route_handlers
            if match_all(kwargs, route)
        )


def match_all(target, patterns):
    return all(
        match(target.get(key), pattern)
        for key, pattern in patterns.items()
    )


def match(target, pattern):
    if target is None:
        return False
    if isinstance(pattern, RegexType):
        return pattern.search(target)
    return pattern == target


class Printer:
    def __init__(self, name):
        self._name = name

    def write(self, **kwargs):
        print(self._name, kwargs)


if __name__ == '__main__':
    d = Demultiplexer()

    left_handler = Printer("left")
    right_handler = Printer("right")
    any_handler = Printer("any")

    d.add_route_handler(left_handler, tag='route-left')
    d.add_route_handler(right_handler, tag='route-right')
    d.add_route_handler(any_handler, tag=re.compile('.*'))

    d.write(message="foo", tag='route-left')
    d.write(message="bar", tag='route-right')
