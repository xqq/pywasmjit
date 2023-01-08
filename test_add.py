from pywasmjit import wasmjit


@wasmjit
def test_add(x: int, y: int):
    a = x
    b = y
    result = a + b
    print(result)
    return result


ret = test_add(114, 514)
print(ret)

ret = test_add(1919, 810)
print(ret)
