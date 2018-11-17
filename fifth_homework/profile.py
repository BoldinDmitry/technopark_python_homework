import time
import types


def function_decorator(func, class_name=None):
    def new_function(*args, **kwargs):
        if not class_name:
            print("'{}' started".format(func.__name__))
        else:
            print("'{}.{}' started".format(class_name, func.__name__))

        started = time.time()
        for_return = func(*args, **kwargs)
        finished = time.time() - started

        if not class_name:
            print("'{}' finished in {}".format(func.__name__, finished))
        else:
            print("'{}.{}' finished in {}".format(class_name, func.__name__, finished))

        return for_return
    return new_function


def class_decorator(klass):
    class_name = klass.__name__

    for method_name in klass.__dict__:
        method = getattr(klass, method_name)

        if callable(method):
            new_method = function_decorator(method, class_name)
            setattr(klass, method_name, new_method)
    return klass


def profile(obj):
    if isinstance(obj, types.FunctionType):
        obj = function_decorator(obj)
    else:
        obj = class_decorator(obj)

    return obj


@profile
def foo():
    pass


@profile
class Bar:
    def __init__(self):
        pass

    def a(self, d):
        print(d)


foo()
Bar().a(1)
