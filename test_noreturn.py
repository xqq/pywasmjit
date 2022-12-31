from pywasmjit import wasmjit


def test_noreturn(x: int, y: int):
    m = x + y + 114 + 514
    n = 114.514 + 1919.810
    if m == 1919:
        x = 810
        return
    return


jit_func = wasmjit(test_noreturn)


# jit_func()
