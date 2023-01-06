from pywasmjit import wasmjit


@wasmjit
def test_output_float(x: float):
    print(x)


@wasmjit
def test_noreturn(x: int, y: int):
    m = x + y + 114 + 514
    n = 114.514 + 1919.810
    if m == 3357:
        x = 810
        test_output_float(n)
        return
    return


test_output_float(114.514)

test_noreturn(1919, 810)
