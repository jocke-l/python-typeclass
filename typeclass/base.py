import builtins
import inspect

from pyparsing import (
    alphas, infixNotation, opAssoc, Suppress, Word, StringStart, StringEnd
)

from typeclass.utils import curry


def signature(sig):
    scope = inspect.stack()[1][0].f_globals
    return Signature(sig, scope)


class Signature:
    def __init__(self, sig, scope):
        self.scope = scope

        if isinstance(sig, tuple):
            self._sig = sig
        elif isinstance(sig, str):
            self._sig = self._signature_from_string(sig)
        else:
            raise TypeError("'sig' is not tuple or str")

    def __call__(self, func):
        curried = curry(func)
        curried.signature = self

        return curried

    @classmethod
    def from_args(cls, args):
        # TODO: Recursive signature (i.e. function arguments)
        def type_name(obj):
            return type(obj).__name__

        sig = tuple(map(type_name, args))

        return cls(sig)

    def _signature_from_string(self, sig_string):
        def process_parsed_signature(sig):
            for element in sig:
                if isinstance(element, str):
                    from_builtins = getattr(builtins, element, element)
                    yield self.scope.get(element, from_builtins)
                elif isinstance(element, list):
                    yield tuple(process_parsed_signature(element))

        arrow = '->'
        arrow_expr = infixNotation(
            Word(alphas),
            [(Suppress(arrow), 2, opAssoc.RIGHT)]
        )

        parser = StringStart() + arrow_expr + StringEnd()

        result = parser.parseString(sig_string).asList()[0]

        return tuple(process_parsed_signature(result))
