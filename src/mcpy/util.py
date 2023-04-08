import contextlib


@contextlib.contextmanager
def scoped_setattr(instance, **kwargs):
    old_values = {}
    for attr, value in kwargs.items():
        old_values[attr] = getattr(instance, attr)
        setattr(instance, attr, value)
    yield instance
    for attr, value in old_values.items():
        setattr(instance, attr, value)
