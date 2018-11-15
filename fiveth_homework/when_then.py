class WhenThenException(Exception):
    """
    This Exception raises when no function with @then or @when decorators found
    """
    pass


class WhenThenList:
    def __init__(self):
        self.when_then_functions = []
        self.when_then_pair = []

    def add_when(self, when_func):
        if not self.when_then_pair:
            self.when_then_pair.append(when_func)
        else:
            error_message = "No function with @then decorator found after {} function"
            raise WhenThenException(
                error_message.format(self.when_then_pair[0].__name__)
            )

    def add_then(self, then_func):
        if self.when_then_pair:
            self.when_then_pair.append(then_func)
            self.when_then_functions.append(self.when_then_pair)
            self.when_then_pair = []
        else:
            error_message = "No function with @when decorator found before {} function"
            raise WhenThenException(
                error_message.format(then_func.__name__)
            )

    def __iter__(self):
        for when_then_pair in self.when_then_functions:
            yield when_then_pair


def whenthen(func):
    func.when_then_list = WhenThenList()

    def when(when_func):
        func.when_then_list.add_when(when_func)

    def then(then_func):
        func.when_then_list.add_then(then_func)

    def decorator(*args, **kwargs):
        for when_func, then_func in func.when_then_list:
            if when_func(*args, **kwargs):
                return then_func(*args, **kwargs)
        return func(*args, **kwargs)

    decorator.when = when
    decorator.then = then

    return decorator
