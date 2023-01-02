from pywasmjit import wasmjit


def test_add(x: int, y: int) -> int:
    a = x + y
    result = -a
    b = False
    c = not b
    if c:
        result = -a
    return result


jit_func = wasmjit(test_add)

