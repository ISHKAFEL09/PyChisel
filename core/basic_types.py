import abc

from core.inner_struct import getRefID, Alias
from core.operations import PrimOp


class Width:
    ...


UnknownWidth = Width()


class IntWidth(Width):
    def __init__(self, value: int):
        self.value = value


class Kind:
    def __init__(self, isFlip: bool):
        self.isFlip = isFlip


class UnknownType(Kind):
    def __init__(self, flip: bool):
        super().__init__(flip)


class UIntType(Kind):
    def __init__(self, width: Width, flip: bool):
        super().__init__(flip)
        self.width = width


class SIntType(Kind):
    def __init__(self, width: Width, flip: bool):
        super().__init__(flip)
        self.width = width


class FloatType(Kind):
    def __init__(self, flip: bool):
        super().__init__(flip)


class DoubleType(Kind):
    def __init__(self, flip: bool):
        super().__init__(flip)


class BundleType(Kind):
    def __init__(self, ports: list['Port'], flip: bool):
        super().__init__(flip)
        self.ports = ports


class VectorType(Kind):
    def __init__(self, size: int, kind: Kind, flip: bool):
        super().__init__(flip)
        self.size = size
        self.kind = kind


class Direction:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


INPUT = Direction('input')
OUTPUT = Direction('output')
NO_DIR = Direction('?')


def flipDirection(direction: Direction) -> Direction:
    if direction is INPUT:
        return OUTPUT
    elif direction is OUTPUT:
        return INPUT
    elif NO_DIR:
        return NO_DIR
    else:
        raise ValueError(f'Unknown direction: {direction}')


class Port:
    def __init__(self, idx: str, direction: Direction, kind: Kind):
        self.idx = idx
        self.direction = direction
        self.kind = kind


class Command(abc.ABC):
    ...


class Definition(Command, abc.ABC):
    def __init__(self, idx: str):
        self._idx = idx

    @property
    def idx(self) -> str:
        return self._idx

    @property
    def name(self) -> str:
        return getRefID(self.idx).name


class DefUInt(Definition):
    def __init__(self, idx: str, value: int, width: int):
        super().__init__(idx)
        self.value = value
        self.width = width


class DefSInt(DefUInt):
    def __init__(self, idx: str, value: int, width: int):
        super().__init__(idx, value, width)


class DefFloat(Definition):
    def __init__(self, idx: str, value: float):
        super().__init__(idx)
        self.value = value


class DefMInt(Definition):
    def __init__(self, idx: str, value: str, width: int):
        super().__init__(idx)
        self.value = value
        self.width = width


class DefPrim(Definition):
    def __init__(self, idx: str, kind: Kind, op: PrimOp, args: list[Alias], lits: list[int]):
        super().__init__(idx)
        self.kind = kind
        self.op = op
        self.args = args
        self.lits = lits


class DefPrimPad(DefPrim):
    def __init__(self, idx: str, kind: Kind, op: PrimOp, args: list[Alias], lits: list[int]):
        super().__init__(idx, kind, op, args, lits)


class DefWire(Definition):
    def __init__(self, idx: str, kind: Kind):
        super().__init__(idx)
        self.kind = kind


class DefRegister(Definition):
    def __init__(self, idx: str, kind: Kind):
        super().__init__(idx)
        self.kind = kind


class DefMemory(Definition):
    def __init__(self, idx: str, kind: Kind, size: int):
        super().__init__(idx)
        self.kind = kind
        self.size = size


class DefAccessor(Definition):
    def __init__(self, idx: str, source: Alias, direction: Direction, index: Alias):
        super().__init__(idx)
        self.source = source
        self.direction = direction
        self.index = index


class DefInstance(Definition):
    def __init__(self, idx: str, module: str):
        super().__init__(idx)
        self.module = module


class Conditionally(Command):
    def __init__(self, pred: Alias, conseq: Command, alt: Command):
        self.pred = pred
        self.conseq = conseq
        self.alt = alt


class Begin(Command):
    def __init__(self, body: list[Command]):
        self.body = body


class Connect(Command):
    def __init__(self, loc: Alias, exp: Alias):
        self.loc = loc
        self.exp = exp


class ConnectPad(Command):
    def __init__(self, loc: Alias, exp: Alias):
        self.loc = loc
        self.exp = exp


class ConnectInit(Command):
    def __init__(self, loc: Alias, exp: Alias):
        self.loc = loc
        self.exp = exp


class ConnectInitIndex(Command):
    def __init__(self, loc: Alias, index: int, exp: Alias):
        self.loc = loc
        self.index = index
        self.exp = exp


class Component:
    def __init__(self, name: str, ports: list[Port], body: Command):
        self.name = name
        self.ports = ports
        self.body = body


class Circuit:
    def __init__(self, components: list[Component], main_body: str):
        self.components = components
        self.main_body = main_body


class EmptyCommand(Command):
    ...


NoLits: list[int] = list()


if __name__ == '__main__':
    print(isinstance(EmptyCommand(), Command))
    i = IntWidth(3)
    print(i.value)
    print(isinstance(i, Width))

    uint = DefUInt('uint', 0, 3)
    print(uint.value, uint.idx, uint.width, uint.name)

    uint = DefSInt('sint', 0, 3)
    print(uint.value, uint.idx, uint.width, uint.name)

    print(INPUT, OUTPUT, NO_DIR)

    print(flipDirection(INPUT))
