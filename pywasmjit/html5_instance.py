from .exec_instance import ExecInstance


class HTML5Instance(ExecInstance):
    def __init__(self, buf: bytes):
        super().__init__(buf)

    def exec_function(self, func_name, *args):
        pass
