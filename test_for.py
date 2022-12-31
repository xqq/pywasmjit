from pywasmjit import wasmjit


def test_for(n: int) -> int:
    sum = 0
    for i in range(n + 1):
        sum += 1
    return sum + 1


jited = wasmjit(test_for)
