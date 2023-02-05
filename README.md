# pywasmjit

An experimental JIT compiler that compiles Python to WebAssembly on the fly.

This project is made for my undergraduate thesis.

## Usage
This library is designed to be used under [PyScript][] / [Pyodide][] web environment.

Import this library and just add `@wasmjit` decorator to your function to speed up it's execution.

[PyScript]: https://pyscript.net/
[Pyodide]: https://pyodide.org/

## Features
- Basic arithmetic operators, compare operators
- `int`, `float`, `bool` type
- `if` expression
- `while` expression
- `for` expression
- Multiple function declarations / function calling / recursive function calling
- Callback to python functions by adding `@wasmreg`

## Demo
https://xqq.github.io/pywasmjit/demo/

## Performance
Tested under Apple M1 Pro, Google Chrome 111.0.5563.8
```bash
test_for(100000000) = 200000000, elapsed: 36.200000000008004 ms
test_for_nojit(100000000) = 200000000, elapsed: 13258.899999999925 ms
rate: 366.2679558010219

test_while_jited(100000000) = 100000000, elapsed: 31.50000000005093 ms
test_while_nojit(100000000) = 100000000, elapsed: 9332.700000000044 ms
rate: 296.27619047571284

is_prime(169941229) = True, elapsed: 119.80000099993049 ms
is_prime_nojit(169941229) = True, elapsed: 24960.000000000036 ms
rate: 208.34724367001064

fibonacci(40) = 102334155, elapsed: 356.7999999997937 ms
fibonacci_nojit(40) = 102334155, elapsed: 33019.399998999914 ms
rate: 92.54316143222815
```

## Build for web
Prepare Pyodide build environment by [following this article][] and then hit
```bash
pyodide build
```

The produced wheel file will be placed in the dist/ folder. Use `pyodide.loadPackage()` to load it.

[following this article]: https://pyodide.org/en/stable/development/building-and-testing-packages.html
## Testing under native Python

Install 3rdparty dependencies

```bash
pip3 install wasmer wasmer_compiler_cranelift
```

Run test scripts, just hit `python3 test_***.py`, e.g.
```bash
python3 test_add.py
```

## License
MIT

## Special thanks
Inspired by [pyjiting][] and [wasmfun][]

[pyjiting]: https://github.com/LanceMoe/pyjiting
[wasmfun]: https://github.com/almarklein/wasmfun
