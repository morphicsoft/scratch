import datetime
import sys
import traceback
from multiprocessing import Process, Manager

import enum
from queue import Empty


def log_worker(log_q, logger):
    """
    log_worker takes log items from an input multiprocessing Queue and passes them onto another logger
    Intended to be used in a distributed logging scenario, where multiple multiprocesses need to aggregate
    their logging to a central sink, such as a file. In this scenario, all of the processes would log to the
    queue via MpQueueLogger, and this worker would write the items to another logger, such as a FileLogger.

    The log_worker terminates once a 'None' value is received, which should be done by a controlling process.

    :param log_q: the multiprocessing Queue to poll for log items.
    :param logger: the output logger to forward on to.
    :return:
    """
    do_loop = True

    while do_loop:
        try:
            log_item = log_q.get()
            if log_item is None:  # None indicates the owning process wants the log_worker to finish
                do_loop = False
            else:
                logger.log(**log_item)
        except Empty:
            do_loop = False

""" TODO:

Enable a logger to be passed around to various classes/functions/processes and for each location to setup a unique
context which is used to identify log output.
"""


class Level(enum.Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


def merge_context(parent, child):
    result = {}
    result.update(child)
    if parent:
        result['parent'] = parent
    return result


def flatten_context(context):
    """
    Given a context hierarchy (which is a dictionary) potentially containing parent contexts, produce a new dict, where
    each value with a corresponding key in the parent is 'flattened' (reduced) in order parent->child

    E.g. {'name': 'X', 'parent': {'name': 'Y'}} becomes {'name': 'Y.X'}
    """

    separator = '.'

    def reduce_dict_value(context, k):
        """
        Given the specified key within the context hierarchy, flatten out ('reduce') the corresponding values up the
        context hierarchy. E.g. if we have a context {'name': 'X', 'parent': {'name': 'Y'}} then return
        the value Y.X

        :param context: the root of the context hierarchy
        :param k: the key of the value to be reduced
        :return:
        """
        accum = []

        def recurse(context, k, accum):
            """
            Do a depth-first traversal of the context hierarchy and accumulate the values into the 'accum' list.
            """
            if 'parent' in context:
                recurse(context['parent'], k, accum)

            if k in context:
                accum.append(context[k])

            return accum

        recurse(context, k, accum)

        return separator.join(accum)

    return {k: reduce_dict_value(context, k) for k, v in context.items() if not k == 'parent'}


def context_as_is(context):
    return {k: v for k, v in context.items() if not k == 'parent'}


def make_context_flatmap(*selected, separator=None):
    """
    A function which returns a context flattener that references a list of selected context keys to be flattened.
    """

    if not selected:
        selected = ['*']
    separator = separator or '.'

    def context_flatmap(context):
        """
        Copy of flatten_context (above) but only flattens values for keys specfied in 'selected'
        """
        def reduce_dict_value(context, k):
            accum = []

            def recurse(context, k, accum):
                if 'parent' in context:
                    recurse(context['parent'], k, accum)

                if k in context:
                    accum.append(context[k])

                return accum

            recurse(context, k, accum)

            return separator.join(accum)

        return {k: reduce_dict_value(context, k) if k in selected or '*' in selected else v
                for k, v in context.items() if not k == 'parent'}

    return context_flatmap


class Logger(object):
    """
    Base logger class, sets out the API for logging. Log entries are structured into a dictionary which includes:

    1. Any key-value details provided at logger construction time as context (included in all log entries).
    2. The level, text message and timestamp (in ISO format).
    3. Any adhoc key-value details provided when logger.log is called, provided as context.

    Subclasses should override _write_to_log, which is called with the details dictionary created as per 1, 2 & 3.
    Subclasses may override end_logging, which is always called on logger destruction, and optionally may be
    directly called by a client as needed. For example, MpQueueLogger writes log output to a multiprocessing queue,
    end_logging is used to signal that the log queue is no longer needed (by this process). Could also be used
    for buffered logging output (for example).

    Each subclass is at liberty to decide how to format the details dictionary and where to route output.
    """

    def __init__(self, level=None, context_reducer=None, **context):
        level = level or 'INFO'
        self._reduce_context = context_reducer or flatten_context
        self._level = level
        self.set_level(level)
        self._context = context
        self._next = None
        self._parent = None

    def new(self, **context):
        new_logger = self.clone()
        new_logger._context = merge_context(self._context, context)
        new_logger.set_parent(self)
        return new_logger

    def top(self):
        p = self
        while p._parent:
            p = p._parent
        return p

    def clone(self):
        return self.__class__(self._level, **self._context)

    def set_level(self, level):
        """
        Sets the filtering level of this logger, either in string (preferred) or int format. See the Level enum
        class for valid log levels.

        :param level: a string representing the log level, e.g. "WARNING"
        :return:
        """
        if isinstance(level, Level):
            self._level = level
        elif type(level) is int:
            self._level = Level(level)
        else:
            self._level = Level[level]

    def set_parent(self, parent):
        self._parent = parent

    def chain(self, logger):
        """
        Allows loggers to be 'chained' so that a log message goes to more than one logger.

        :param logger: A logger instance to be called after this logger
        :return:
        """
        # if self._next is None:
        #     self._next = logger
        # else:
        #     self._next.chain(logger)
        # return self
        logger.set_parent(self)
        return self

    def exception(self, exc):
        """
        Convenience method for formatting and logging an exception.

        :param exc: the caught exception to be logged.
        :return:
        """
        return self.log("Exception: {}".format(exc), level="ERROR", exc_info=traceback.format_exc())

    def log(self, msg, level="INFO", **context):
        level = Level[level] if level else self._level
        if level.value < self._level.value:
            return

        details = {
            'level': level.name,
            'msg': msg,
            'timestamp': datetime.datetime.now().isoformat()
        }
        details.update(self._context)
        # Explicitly provided context takes precedence over logger-wide context
        # details.update(self._context)
        details.update(context)

        details = self.top()._reduce_context(details)
        self._write_to_log(details)
        # self._log_next(msg, level, **kwargs)

    def _log_next(self, msg, level, **kwargs):
        if self._parent:
            self._parent.log(msg, level.name, **kwargs)

    def _write_to_log(self, details):
        raise NotImplementedError()

    # TODO: end_logging is a bodge, would be better if the controlling process could determine when processing is done
    def end_logging(self):
        pass


class NullLogger(Logger):
    """
    A logger which does nothing with the log output. Useful for suppressing logging.
    """

    def _write_to_log(self, details):
        pass


class StreamLogger(Logger):

    def __init__(self, stream, level=None, **context):
        super(StreamLogger, self).__init__(level, **context)
        self._stream = stream

    def clone(self):
        return self.__class__(self._stream, self._level, **self._context)

    def _write_to_log(self, details):
        log_line = str(details) + "\n"
        self._stream.write(log_line)


class PrintLogger(StreamLogger):
    """
    A minimal logger implementation which routes log output to stdout via the print() function.
    Use this instead of directly using print() as it a) formats the output and b) can easily
    be substituted with another logger implementation.
    """

    def __init__(self, level=None, **context):
        super(PrintLogger, self).__init__(sys.stdout, level, **context)


class FileLogger(StreamLogger):

    def __init__(self, path, level=None, **context):
        stream = open(path, "a", 0)
        super(FileLogger, self).__init__(stream, level, **context)


class MpQueueLogger(Logger):
    """
    logger implementation which routes log entries to a multiprocessing queue. The queue must be provided in the ctor.
    """

    def __init__(self, q, level=None, **context):
        super(MpQueueLogger, self).__init__(level, **context)
        self._q = q

    def _write_to_log(self, details):
        self._q.put(details)

    def end_logging(self):
        self._q.put(None)

    def clone(self):
        return self.__class__(self._q, self._level, **self._context)


class AutomatedMpQueueLogger(MpQueueLogger):
    """
    A specialisation of MpQueueLogger which creates a logging queue and starts up a log worker, encapsulating
    a common pattern. Introduces start and join methods which delegate to the underlying log worker process.

    Must chain another logger before starting, so that queued log output can be routed somewhere. E.g:

        mp_logger = AutomatedMpQueueLogger()
        print_logger = PrintLogger()

        mp_logger.chain(print_logger)
        mp_logger.start()

        p = Process(target=some_func, args=(logger=mp_logger,))
        p.start()

        // ... run processes which do logging ...

        p.join()

        logger.end_logging()
        mp_logger.join()

    Note that it's possible to pass the logger across a process boundary, including to functions within a process
    pool.
    """
    def __init__(self, level=None, **context):
        # Use a managed queue so the logger can be passed to functions within process pools
        m = Manager()
        q = m.Queue()
        super(AutomatedMpQueueLogger, self).__init__(q, level, **context)
        self._worker = None

    def start(self):
        if self._next is None:
            raise Exception("No log chain exists.")
        self._next.log("Starting the log worker.")
        self._worker = Process(target=log_worker, args=(self._q, self._next))
        self._worker.start()

    def join(self):
        self._worker.join()

    def terminate(self):
        self._worker.terminate()

    def _log_next(self, msg, level, **context):
        # Disable the log chaining here, as the "next" logging is done in the worker process
        pass

    def __getstate__(self):
        # pickle everything but the worker
        return {'_context': self._context, '_level': self._level, '_q': self._q}

    def __setstate__(self, state):
        self.__dict__.update(state)

    def clone(self):
        # Return a MpQueueLogger instance as we don't want to duplicate the queue or worker
        return MpQueueLogger(self._q, self._level, **self._context)


class BufferedLogger(Logger):
    """
    logger implementation which keeps log entries in a list buffer until explicitly cleared.
    The buffer is exposed via a buffer property
    """

    def __init__(self, level=None, **context):
        super(BufferedLogger, self).__init__(level, **context)
        self.buffer = []

    def _write_to_log(self, details):
        self.buffer.append(details)

    def clear(self):
        self.buffer = []

    def end_logging(self):
        self.buffer = []


class LoggingMixin(object):
    """
    A convenience mixin class for injecting logging methods into any class needing access to logging facilities.
    Can optionally provide a logger instance and/or a level specification to the constructor. If not provided,
    these will default to PrintLogger and "INFO" respectively.

    It is also possible to override either the logger or level at runtime using set_logger or set_level.
    """
    def __init__(self, logger=None, level=None):
        self._logger = logger
        self._level = level

    @property
    def logger(self):
        if self._logger is None:
            self._logger = PrintLogger(self._level or 'INFO')
        return self._logger

    def set_logger(self, logger):
        self._logger = logger
        return self

    def set_level(self, level):
        self._level = level
        if self._logger:
            self._logger.set_level(level)
        return self

    def log(self, *args, **context):
        self.logger.log(*args, **context)
        return self

    def exception(self, *args, **context):
        self.logger.exception(*args, **context)
        return self

    def end_logging(self):
        self.logger.end_logging()


if __name__ == '__main__':

    context_flattener = make_context_flatmap()
    p1 = StreamLogger(sys.stdout, name='logger_1', foo='bar', thing='stuff', context_reducer=context_flattener)
    p1.log("Hello 1")

    p2 = p1.new(name='logger_2', foo='baz', otherthing='otherstuff')
    p2.log("Hello 2")

    p3 = p2.new(name='logger_3')
    p3.log("Hello 3")
    p3.log("Hello 4", foo='qux')
