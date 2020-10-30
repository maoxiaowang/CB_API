import functools


def change_auto_id(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        self.auto_id = self.__class__.__name__.lower() + '_%s'
        return func(self, *args, **kwargs)

    return inner
