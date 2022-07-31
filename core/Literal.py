import re


def parseLit(x: str) -> tuple[str, str, int]:
    if not re.match(r'^[01?_]+$', x):
        raise ValueError(f'Literal: {x} contains illegal character, only [01?_] expected.')
    x = x.replace('_', '')
    mask = x.replace('0', '1').replace('?', '0')
    bits = x.replace('?', '0')
    return bits, mask, len(x)


def toLitVal(x: str, base: int = None) -> int:
    if base is None:
        return int(x[1:], 16)
    else:
        x = x.replace('_', '').lower()
        if not re.match(r'^[\da-f?]+$', x):
            raise ValueError(f'Literal: {x} contains illegal character, only [0-9A-Fa-f?] expected.')
        return int(x, base)


def string2Val(base: str, x: str) -> int:
    match base:
        case 'x':
            return toLitVal(x, 16)
        case 'd':
            return toLitVal(x, 10)
        case 'h':
            return toLitVal(x, 16)
        case 'b':
            return toLitVal(x, 2)
        case 'o':
            return toLitVal(x, 8)
        case _:
            return -1


if __name__ == '__main__':
    print(toLitVal('5a5a_a5a5', 16))
    print(string2Val('h', 'aa'))
