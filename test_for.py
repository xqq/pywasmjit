import time
import pywasmjit
from pywasmjit import wasmjit


@wasmjit
def test_for(n: int):
    for _ in range(n):
        n += 1
    return n


def test_for_nojit(n: int):
    for _ in range(n):
        n += 1
    return n


pywasmjit.warmup()

start_time = time.time()
result = test_for(100000000)
elapsed = (time.time() - start_time) * 1000
print(f'test_for(100000000) = {result}, elapsed: {elapsed} ms')

start_time = time.time()
result = test_for_nojit(100000000)
elapsed_nojit = (time.time() - start_time) * 1000
print(f'test_for_nojit(100000000) = {result}, elapsed: {elapsed_nojit} ms')
print('rate:', 'Infinite' if elapsed == 0 else elapsed_nojit / elapsed)
