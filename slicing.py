

class C:
    def __init__(self, items=None):
        self._items = items or []

    def get(self, items):
        if items is Ellipsis:
            return self._items
        return self._items[items]

    def append(self, item):
        self._items.append(item)


if __name__ == '__main__':

    c = C()
    c.append(1)
    c.append(2)
    c.append(3)

    print(c.get(...))
