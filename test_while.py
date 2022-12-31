from re import I
from pywasmjit import wasmjit


def test_while(x: int) -> int:
    i = 0
    while i < x:
        i = i + 1
    return i


jited = wasmjit(test_while)
