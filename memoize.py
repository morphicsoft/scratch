from functools import wraps


def memoize(f):
    cache = {}

    @wraps(f)
    def wrapper(*args, **kwargs):
        keyword_items = tuple(kwargs.items())
        cache_key = (args, keyword_items)
        if cache_key in cache:
            return cache[cache_key]
        result = f(*args, **kwargs)
        cache[cache_key] = result
        return result

    return wrapper
