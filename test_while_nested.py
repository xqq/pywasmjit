from pywasmjit import wasmjit


@wasmjit
def test_while(x: int) -> int:
    ret = 0
    i = 0
    while i < x:
        i += 1
        j = 0
        while True:
            j += 1
            if j >= 10:
                ret += j
                break
    return ret


print(test_while(114514))
