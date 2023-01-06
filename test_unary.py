from pywasmjit import wasmjit

@wasmjit
def test_add(x: int, y: int) -> int:
    a = x + y
    result = -a
    b = False
    c = not b
    if c:
        result = -a
    return result


print(test_add(114, 514))
