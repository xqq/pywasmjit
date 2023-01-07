DEBUG = False

def debug_print(fmt: str, *args):
    if not DEBUG:
        return
    print('=' * 80)
    print(fmt, *args)


class FunctionSignature:
    __slots__ = ['params', 'return_type']

    def __init__(self, params: list[str], return_type: str):
        self.params: list[str] = params
        self.return_type: str = return_type
