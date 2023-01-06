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
cost_time_ms = (time.time() - start_time) * 1000
print('test_for(100000000) =', result, f'(elapsed time: {cost_time_ms} ms)')

start_time = time.time()
result = test_for_nojit(100000000)
cost_time_ms_nojit = (time.time() - start_time) * 1000
print('test_for_nojit(100000000) =', result, f'(elapsed time: {cost_time_ms_nojit} ms)')
print('rate:', 'Infinite' if cost_time_ms == 0 else cost_time_ms_nojit / cost_time_ms)
