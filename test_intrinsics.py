from pywasmjit import wasmjit


def test_intrinsics(n: int):
    f = float(n)
    b = bool(n)
    i = int(f)
    print(i)


jited = wasmjit(test_intrinsics)
