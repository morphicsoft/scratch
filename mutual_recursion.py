from enum import Enum


class Command(Enum):
    OPEN = 0
    CLOSE = 1
    UP = 2
    DOWN = 3
    DONE = 4


def elevator(*commands):
    """
    A port of the mutually recursive functions example from joy of clojure 2nd ed.
    """
    def ff_open(*commands):
        print("First-floor opened")
        c, *r = commands
        if c == Command.CLOSE:
            return ff_closed(*r)
        elif c == Command.DONE:
            return True
        else:
            return False

    def ff_closed(*commands):
        print("First-floor closed")
        c, *r = commands
        if c == Command.OPEN:
            return ff_open(*r)
        elif c == Command.UP:
            return sf_closed(*r)
        else:
            return False

    def sf_closed(*commands):
        print("Second-floor closed")
        c, *r = commands
        if c == Command.OPEN:
            return sf_open(*r)
        elif c == Command.DOWN:
            return ff_closed(*r)
        else:
            return False

    def sf_open(*commands):
        print("Second-floor open")
        c, *r = commands
        if c == Command.CLOSE:
            return sf_closed(*r)
        elif c == Command.DONE:
            return True
        else:
            return False

    return ff_open(*commands)


print(elevator(Command.CLOSE, Command.OPEN, Command.CLOSE, Command.UP, Command.OPEN, Command.OPEN, Command.DONE))
print(elevator(Command.CLOSE, Command.UP, Command.OPEN, Command.CLOSE, Command.DOWN, Command.OPEN, Command.DONE))

