from functools import wraps
import time


def Memoize(func):
    #cache
    cache = dict()
    @wraps(func)
    def wrapped(*args,**kwargs):
        key = str(func) + str(args) + str(kwargs)
        #if key not in cache
        if cache.get(key) is None:
            result = func(*args, **kwargs)
            cache[key] = result
        return cache[key]
    return wrapped


def Timer(f):
    @wraps(f)
    def wrapped(*args,**kwargs):
        s = time.time()
        result = f(*args,**kwargs)
        e = time.time()
        print(f'Function {f}: {e-s} seconds')
        return result
    return wrapped