DEBUG = True


def debug_print(fmt: str, *args):
    if not DEBUG:
        return
    print('=' * 80)
    print(fmt, *args)
