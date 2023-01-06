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

start_time = time.time()
result = jited(100000000)
cost_time_ms = (time.time() - start_time) * 1000
print('test_while_jited(100000000) =', result, f'(elapsed time: {cost_time_ms} ms)')

start_time = time.time()
result = test_while(100000000)
cost_time_ms_nojit = (time.time() - start_time) * 1000
print('test_while_nojit(100000000) =', result, f'(elapsed time: {cost_time_ms_nojit} ms)')
print('rate:', 'Infinite' if cost_time_ms == 0 else cost_time_ms_nojit / cost_time_ms)
