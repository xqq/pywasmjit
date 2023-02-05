from pywasmjit import wasmjit

@wasmjit
def test_intrinsics(n: int):
    f = float(n)
    b = bool(n)
    i = int(f)
    print(f)
    return i


print(test_intrinsics(114514))

