import inspect


def curry(func):
    return Currying(func)


class Currying:
    def __init__(self, function, args=None):
        self._function = function
        self._args = args or []
        self._num_args = len(inspect.signature(function).parameters)

    def __repr__(self):
        return '<{}: function={} args={} num_args={}>'.format(
            type(self).__name__,
            self._function.__name__,
            self._args,
            self._num_args
        )

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
