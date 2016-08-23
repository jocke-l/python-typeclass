import builtins
import inspect

from pyparsing import alphas, opAssoc
from pyparsing import infixNotation
from pyparsing import Suppress, StringStart, StringEnd, Word


def signature(sig):
    scope = inspect.stack()[1][0].f_globals
    return Signature(sig, scope)



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

