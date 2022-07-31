import abc
from collections import abc as collect_abc


_refMap: collect_abc.MutableMapping[str, 'Immediate'] = dict()


def _genSys():
    def _innerGenSys():
        counter = -1
        cname = ''
        while True:
            name = yield cname
            counter += 1
            cname = f'{name}_{counter}'
    tmp = _innerGenSys()
    next(tmp)
    return tmp


genSys = _genSys().send


class Immediate(abc.ABC):
    @property
    @abc.abstractmethod
    def fullname(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...


class Alias(Immediate):
    def __init__(self, idx: str):
        self.idx = idx

    @property
    def fullname(self) -> str:
        return getRefID(self.idx).fullname

    @property
    def name(self) -> str:
        return getRefID(self.idx).name


class Ref(Immediate):
    def __init__(self, name: str):
        self.Name = name

    @property
    def fullname(self) -> str:
        return self.Name

    @property
    def name(self) -> str:
        return self.Name


class Slot(Immediate):
    def __init__(self, imm: Immediate, name: str):
        self.imm = imm
        self.Name = name

    @property
    def fullname(self) -> str:
        return self.Name if self.imm.fullname == 'self' else f'{self.imm.fullname}.{self.Name}'

    @property
    def name(self) -> str:
        return self.Name


class Index(Immediate):
    def __init__(self, imm: Immediate, value: int):
        self.imm = imm
        self.value = value

    @property
    def name(self) -> str:
        return f'.{self.value}'

    @property
    def fullname(self) -> str:
        return f'{self.imm.fullname}.{self.value}'


def setRefID(idx: str, name: str, overwrite: bool) -> None:
    if overwrite or idx not in _refMap:
        _refMap[idx] = Ref(name)


def setFieldID(parent_id: str, idx: str, name: str) -> None:
    _refMap[idx] = Slot(Alias(parent_id), name)


def setIndexID(parent_id: str, idx: str, index: int) -> None:
    _refMap[idx] = Index(Alias(parent_id), index)


def getRefID(idx: str) -> Immediate:
    if idx in _refMap:
        return _refMap[idx]
    else:
        ref = Ref(genSys('T'))
        _refMap[idx] = ref
        return ref
