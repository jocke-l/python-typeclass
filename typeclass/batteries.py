import typeclass
from typeclass import signature


class Show:
    show = signature('a -> str')


@typeclass.instance(Show, int)
class ShowInt:
    @signature('int -> str')
    def show(a):
        return str(a)


@typeclass.instance(Show, float)
class ShowFloat:
    @signature('float -> str')
    def show(a):
        return str(a)
