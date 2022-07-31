from abc import ABC
from functools import cached_property

from core.utils import *
import driver
from core.params import Parameters
from Wire import Wire


class Id(ABC):
    def __init__(self):
        self.idx = genSys('id')
        self._isDefined = False

    def defined(self):
        self._isDefined = True
        return self

    @property
    def isDefined(self):
        return self._isDefined


class Data(Id, ABC):
    def __init__(self, direction: Direction):
        super().__init__()
        self.mod = moduleStack[-1]
        self._isFlipVar = direction is INPUT
        self._isReg = False

    @abc.abstractmethod
    def toType(self) -> Kind: ...

    @abc.abstractmethod
    def cloneType(self) -> 'Data': ...

    @abc.abstractmethod
    def cloneTypeWidth(self, width: int) -> 'Data': ...

    def setLitValue(self, x: int) -> None:
        ...

    @abc.abstractmethod
    def getWidth(self) -> int: ...

    @abc.abstractmethod
    def flatten(self) -> list['Data']: ...

    @abc.abstractmethod
    def collectElms(self) -> None: ...

    @property
    def isFlip(self) -> bool:
        return self._isFlipVar

    @property
    def direction(self) -> Direction:
        return INPUT if self.isFlip else OUTPUT

    def setDirection(self, direction: Direction) -> None:
        self._isFlipVar = direction is INPUT

    def asInput(self) -> 'Data':
        self.setDirection(INPUT)
        return self

    def asOutput(self) -> 'Data':
        self.setDirection(OUTPUT)
        return self

    def flip(self) -> 'Data':
        self._isFlipVar = not self._isFlipVar
        return self

    @cached_property
    def ref(self) -> Alias:
        return Alias(self.idx)

    def __ilshift__(self, other: 'Data') -> 'Data':
        pushCommand(Connect(self.ref, other.ref))
        return self

    @property
    def name(self) -> str:
        return getRefID(self.idx).name

    @property
    def debugName(self) -> str:
        return f'{self.mod.debugName}.{self.name}'

    @property
    def litValue(self) -> int:
        return -1

    @property
    def isLitValue(self) -> bool:
        return False

    def fromBits(self, n: 'Data') -> 'Data':
        res = self.cloneType()
        _i = 0
        wire = Wire(res)
        for x in reversed(wire.flatten()):
            x <<= n[_i + x.getWidth():_i]
            _i += x.getWidth()
        return res

    def toBits(self) -> 'Data':
        elms = self.flatten()
        return Cat(*elms)

    def makeLit(self, value: int, width: int) -> 'Data':
        from .Bits import Bits
        x = self.cloneType()
        x.fromBits(Bits(value, width))
        return x

    def toBool(self) -> 'Data':
        from .Bool import Bool
        return chiselCast(self, Bool())

    def toPort(self) -> 'Port':
        return Port(self.idx, self.direction, self.toType())

    @property
    def isReg(self):
        return self._isReg

    @property
    def params(self):
        return Parameters.empty if not driver.parStack else driver.parStack[-1]
    
    
class _FakeData(Data):
    def __init__(self):
        from core.Module import Module
        pushModule(Module())
        pushCommands()
        super(_FakeData, self).__init__(NO_DIR)
        
    def cloneType(self) -> 'Data':
        return _FakeData()

    def cloneTypeWidth(self, width: int) -> 'Data':
        pass

    def getWidth(self) -> int:
        pass

    def flatten(self) -> list['Data']:
        pass

    def collectElms(self) -> None:
        pass

    def toType(self) -> Kind:
        pass
