from distutils.core import setup

import setuptools

setup(
    name='pywasmjit',
    version='0.1.0',
    description='Compile Python to WebAssembly on the fly',
    author='xqq',
    author_email='xqq@xqq.im',
    packages=['pywasmjit', 'pywasmjit.wasm'],
    package_dir= {
        'pywasmjit': 'pywasmjit',
        'pywasmjit.wasm': 'pywasmjit/wasm'
    }
)
