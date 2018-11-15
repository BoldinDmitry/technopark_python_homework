import time
import types


def print_working_time(func, klass=None):
    print(func.__name__ + " started")
    started = time.time()

    if klass is None:
        func()
    else:
        func(klass)

    finished = time.time() - started
    print(func.__name__ + " finished in " + str(finished))


def profile(func):
    def new_func():

        if isinstance(func, types.FunctionType):
            print_working_time(func)
        else:
            for method_name, method in func.__dict__.items():
                if isinstance(method, types.FunctionType):
                    print_working_time(method, func)

    return new_func
