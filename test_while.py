import time
from pywasmjit import wasmjit


def test_while(x: int) -> int:
    i = 0
    while i < x:
        i = i + 1
    return i


jited = wasmjit(test_while)

jited(0)
test_while(0)

start_time = time.perf_counter()
result = jited(100000000)
elapsed = (time.perf_counter() - start_time) * 1000
print(f'test_while_jited(100000000) = {result}, elapsed: {elapsed} ms')

start_time = time.perf_counter()
result = test_while(100000000)
elapsed_nojit = (time.perf_counter() - start_time) * 1000
print(f'test_while_nojit(100000000) = {result}, elapsed: {elapsed_nojit} ms')
print('rate:', 'Infinite' if elapsed == 0 else elapsed_nojit / elapsed)
