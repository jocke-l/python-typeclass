import inspect


class Currying:
    def __init__(self, function, args=None):
        self._function = function
        self._args = args or []
        self._num_args = len(inspect.signature(function).parameters)

    def __repr__(self):
        return '{} {}'.format(
            self._function.__name__,
            ' '.join(self._args),
        ).rstrip()

    def __call__(self, *added_args):
        new_args = self._args + list(added_args)
        return type(self)(self._function, new_args)._call_or_return_self()

    def _call_or_return_self(self):
        try:
            return self._function(*self._args)
        except TypeError:
            if len(self._args) > self._num_args:
                raise

            return self


def curry(func):
    return Currying(func)


@curry
def flip(f, a, b):
    return f(b, a)
