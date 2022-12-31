from pywasmjit import wasmjit

def test_add(x: int, y: int) -> int:
    a = x
    b = y
    result = a + b
    return result

jit_func = wasmjit(test_add)

# ret = jit_func(1, 2)
#
# print(ret)
