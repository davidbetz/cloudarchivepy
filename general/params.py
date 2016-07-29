def get_kwarg(self, name, **kwargs):
    return kwargs[name] if name in kwargs else ''

def get_arg(self, name, *args):
    return args[0] if len(args) > 0 else ''