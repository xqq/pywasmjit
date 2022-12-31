from pywasmjit import wasmjit


def test_compare(x: int, y: int):
    if x > y:
        x = x + 1
        return x
    elif x == y:
        y = y + 1
        return y
    else:
        return y + 1


jit_func = wasmjit(test_compare)

