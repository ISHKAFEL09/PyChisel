import functools
import operator
from functools import partial

from core.inner_struct import setIndexID
from core.utils import *
from core.Data import Data
from core.UInt import _UInt, UInt
from core.Bool import _Bool
from core.Mux import PriorityMux, Mux1H


class Aggregate(Data, abc.ABC):
    def __init__(self, direction: Direction):
        super().__init__(direction)

    def cloneTypeWidth(self, width: int) -> Data:
        return self.cloneType()


class VecLikeMix(list):
    @abc.abstractmethod
    def __call__(self, idx: _UInt) -> Data:
        ...

    def forall(self, p: Callable[[Data], _Bool]) -> _Bool:
        return functools.reduce(operator.and_, [p(v) for v in self])

    def exists(self, p: Callable[[Data], _Bool]) -> _Bool:
        return functools.reduce(operator.or_, [p(v) for v in self])

    def count(self, p: Callable[[Data], _Bool]) -> _UInt:
        return PopCount([p(v) for v in self])

    def _indexWhereHelper(self, p: Callable[[Data], _Bool]) -> list[tuple[_Bool, _UInt]]:
        return list(zip([p(v) for v in self], [UInt(x) for x in range(len(self))]))

    def indexWhere(self, p: Callable[[Data], _Bool]) -> Data:
        return PriorityMux(self._indexWhereHelper(p))

    def lastIndexWhere(self, p: Callable[[Data], _Bool]) -> Data:
        return PriorityMux(self._indexWhereHelper(p).reverse())

    def onlyIndexWhere(self, p: Callable[[Data], _Bool]) -> Data:
        return Mux1H(self._indexWhereHelper(p))


class _Vec(Aggregate, VecLikeMix):
    def __init__(self, datas: Iterable[Data], direction: Direction = NO_DIR):
        datas = list(datas)
        super().__init__(direction)
        self.extend(datas)
        self._head = datas[0]

    def isReg(self):
        return self._head.isReg

    def isFlip(self) -> bool:
        isSubFlip = self._head.isFlip
        return not isSubFlip if self._isFlipVar else isSubFlip

    def __call__(self, idx: int | _UInt):
        match idx:
            case int():
                return self[idx]
            case _UInt():
                x = self._head.cloneType()
                pushCommand(DefAccessor(x.defined().idx, Alias(self.idx), NO_DIR, idx.ref))
                return x
            case _:
                raise ValueError(f'int or UInt expect, while get {type(idx)}')

    def toPorts(self) -> list[Port]:
        return [d.toPort() for d in self]

    def toType(self) -> Kind:
        return VectorType(len(self), self._head.toType(), self._isFlipVar)

    def cloneType(self) -> 'Data':
        v = Vec(self._head.cloneType(), len(self))
        v.collectElms()
        return v

    def collectElms(self) -> None:
        for idx, elem in enumerate(self):
            setIndexID(self.idx, elem.idx, idx)
            elem.collectElms()

    def flatten(self) -> list['Data']:
        return functools.reduce(operator.add, [x.flatten() for x in self])

    def getWidth(self) -> int:
        return functools.reduce(operator.add, [x.getWidth() for x in self.flatten()])

    @property
    def length(self):
        return len(self)


def Vec(*args) -> _Vec:
    match args:
        case Data() as gen, int(n):
            return _Vec([gen.cloneType() for _ in range(n)])
        case collections.abc.Iterable() as elms, :
            vec = _Vec([elms[0].cloneType() for _ in range(len(elms))])
            vec.collectElms()
            if vec.isReg():
                raise TypeError(f'Vec of Reg not support')
            pushCommand(DefWire(vec.defined().idx, vec.toType()))
            for i, elm in enumerate(elms):
                pushCommand(ConnectPad(vec(i).ref, elm.ref))
            return vec
        case Data() as elm0, collections.abc.Iterable() as elms:
            return Vec([elm0].extend(list(elms)))
        case _:
            raise ValueError('unsupported usage')


def tabulate(n: int, gen: Callable[[int], Data] = None) -> partial | _Vec:
    if gen is None:
        return partial(tabulate, n)
    else:
        return Vec([gen(i) for i in range(n)])


def fill(n: int, gen: Data = None) -> partial | _Vec:
    if gen is None:
        return partial(fill, n)
    else:
        return tabulate(n, lambda _: gen)


if __name__ == '__main__':
    from core.Data import _FakeData
    v: _Vec = fill(5)(_FakeData())
    print(v)
    print(v.length)
    print(v(3))
    print(v.litValue)
    print(v.toType())
    print(v.cloneType())
