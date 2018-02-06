import time


def get_name(callable):
    if hasattr(callable, '__name__'):
        return callable.__name__
    elif hasattr(callable, '__class__'):
        return callable.__class__.__name__
    else:
        return "callable"


class Retry:

    class RetryFailedError(Exception):
        def __init__(self, name, attempts):
            msg = "{} failed to return successfully after {} attempts".format(name, attempts)
            super(Retry.RetryFailedError, self).__init__(msg)

    class Backoff:
        def __init__(self, delay, factor):
            self._delay = delay
            self._factor = factor
            self._count = 1

        def wait(self):
            delay = self._delay * self._factor ** self._count
            time.sleep(delay)
            self._count += 1

    def __init__(self, f, success, max_attempts, retry_delay, backoff_factor=1):
        self._f = f
        self.name = get_name(f)
        self._success = success
        self.max_attempts = max_attempts
        self._backoff = self.Backoff(retry_delay, backoff_factor)

    def __call__(self, *args, **kwargs):
        attempts = 0

        while True:
            try:
                attempts += 1
                print("Call {} attempt #{}".format(self.name, attempts))
                result = self._f(*args, **kwargs)
                if self._success(result):
                    print("{} returned successfully.".format(self.name))
                    return result
            except Exception as e:
                self._maybe_raise(attempts=attempts, exception=e)
            self._maybe_raise(attempts=attempts)
            self._backoff.wait()

    def _maybe_raise(self, attempts, exception=None):
        if attempts >= self.max_attempts:
            exception = exception or self.RetryFailedError(name=self.name, attempts=attempts)
            raise exception


class Callable:

    def __init__(self):
        self.count = 0

    def __call__(self, i):
        self.count += 1
        print("Call number {}".format(self.count))
        if self.count >= 9:
            raise Exception("Something went wrong")
        return i + 90


if __name__ == '__main__':

    r = Retry(Callable(), success=lambda x: x == 99, max_attempts=10, retry_delay=0.1, backoff_factor=1)
    val = r(8)
    print("Got result", val)
