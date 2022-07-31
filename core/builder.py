import collections.abc
from collections import deque
from core.basic_types import *
from core.inner_struct import genSys
from typing import Callable


components: list[Component] = list()

scopeStack: deque[set[str]] = deque()

switchKeysStack: deque[deque['_Bits']] = deque()

modules: collections.abc.MutableMapping[str, 'Module'] = dict()

moduleStack: deque['Module'] = deque()

componentNames: set[str] = set()

commandStack: deque[list[Command]] = deque()


def scope() -> set[str]:
    return scopeStack[-1]


def switchKeys() -> deque['_Bits']:
    return switchKeysStack[-1]


def pushScope() -> None:
    scopeStack.append(set())
    switchKeysStack.append(deque())


def popScope() -> None:
    scopeStack.pop()
    switchKeysStack.pop()


def addModule(mod: 'Module') -> None:
    modules[mod.id] = mod


def pushModule(mod: 'Module') -> None:
    moduleStack.append(mod)


def getComponent() -> 'Module':
    return moduleStack[0]


def popModule() -> None:
    moduleStack.pop()


def uniqueComponent(name: str, ports: list[Port], body: Command) -> Component:
    ret = Component(genSys(name) if name in componentNames else name, ports, body)
    componentNames.add(name)
    return ret


def commands() -> list[Command]:
    return commandStack[-1]


def pushCommand(cmd: Command) -> None:
    commands().append(cmd)


def toCommand(cmds: list[Command]) -> Command:
    match (len(cmds)):
        case 0:
            return EmptyCommand()
        case 1:
            return cmds[0]
        case _:
            return Begin(cmds)


def pushCommands() -> None:
    commandStack.append(list())


def popCommands() -> Command:
    return toCommand(commandStack.pop())


def collectCommands(f: Callable[[], 'Module']) -> tuple[Command, 'Module']:
    pushCommands()
    ret = f()
    return popCommands(), ret


def build(f: Callable[[], 'Module']) -> tuple[Circuit, 'Module']:
    _, mod = collectCommands(f)
    return Circuit(components, components[-1].name), mod


if __name__ == '__main__':
    print(genSys('id'))
    print(genSys('T'))
    scopeStack.extend([set('a'), set('b'), set('c')])
    print(scope())
    print(scopeStack.pop())
    print(scopeStack.pop())
