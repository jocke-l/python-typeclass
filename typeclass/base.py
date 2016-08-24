import builtins
import inspect
from collections import defaultdict

from pyparsing import alphas, opAssoc
from pyparsing import infixNotation
from pyparsing import Suppress, StringStart, StringEnd, Word

from typeclass.utils import curry


def instance(type_class, data_type):
    def decorator(cls):
        registry.register(cls, type_class, data_type)
        return cls

    return decorator


def signature(sig_string):
    scope = inspect.stack()[1][0].f_globals
    return Signature.from_string(sig_string, scope)


class Signature:
    def __init__(self, takes, returns):
        self.takes = takes
        self.returns = returns

    def __repr__(self):
        if isinstance(self.takes, str):
            takes = self.takes
        elif isinstance(self.takes, type(self)):
            takes = '({})'.format(self.takes)
        else:
            takes = '<{}>'.format(self.takes.__name__)

        if not any((isinstance(self.returns, type(self)),
                    isinstance(self.returns, str))):
            returns = '<{}>'.format(self.returns.__name__)
        else:
            returns = self.returns

        return '{} -> {}'.format(takes, returns)

    def __call__(self, function):
        function = curry(function)
        function.signature = self

        return function

    @classmethod
    def from_string(cls, sig_string, scope):
        def process(node):
            if isinstance(node, str):
                from_builtins = getattr(builtins, node, node)
                return scope.get(node, from_builtins)

            return walk(node)

        def walk(parse_tree):
            return cls(*map(process, parse_tree))

        arrow = '->'
        arrow_expr = infixNotation(
            Word(alphas),
            [(Suppress(arrow), 2, opAssoc.RIGHT)]
        )

        parser = StringStart() + arrow_expr + StringEnd()

        return walk(parser.parseString(sig_string).asList()[0])

    @classmethod
    def from_args(cls, args):
        if len(args) == 1:
            return cls(type(args[0]), 'unknown')
        else:
            return cls(type(args[0]), cls.from_args(args[1:]))

    def matches(self, other):
        type_vars = {}

        def match(a, b):
            if isinstance(a, str) and a not in type_vars:
                type_vars[a] = b

            if isinstance(b, str) and b not in type_vars:
                type_vars[b] = a

            if isinstance(a, type(self)) and isinstance(b, type(self)):
                return match(a.takes, b.takes) and match(a.returns, b.returns)
            elif isinstance(a, str) or isinstance(b, str):
                return type_vars.get(a, a) == b or type_vars.get(b, b) == a
            else:
                return a == b

        return match(self, other)


class Registry:
    _registry = defaultdict(dict)

    def __getattr__(self, name):
        def dispatcher(*args):
            call_signature = Signature.from_args(args)
            for method_signature, method in self._registry[name].items():
                if call_signature.matches(method_signature):
                    return method(*args)

            raise NameError('This function is not in any type class.')

        return dispatcher

    def register(self, instance, type_class, data_type):
        signatures = {
            name: getattr(type_class, name)
            for name in dir(type_class)
            if isinstance(getattr(type_class, name), Signature)
        }

        methods = {
            name: getattr(instance, name)
            for name in dir(instance)
            if hasattr(getattr(instance, name), 'signature')
        }

        if set(signatures) != set(methods):
            raise TypeError(
                "Instance '{}' doesn't match type class '{}'s"
                "definition. Needs '{}'.".format(
                    instnace.__name__,
                    type_class.__name__,
                    ', '.format(signatures)
                )
            )

        for method_name, method in methods.items():
            if method.signature.matches(signatures[method_name]):
                self._registry[method_name][method.signature] = method
            else:
                raise TypeError(
                    "Method '{}' in instance '{}' of "
                    "type class '{}' didn't type-check. "
                    "Expected '{}'. Got '{}'.".format(
                        method.__name__,
                        instance.__name__,
                        type_class.__name__,
                        signatures[method_name],
                        method.signature
                    )
                )


registry = Registry()
