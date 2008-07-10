import os

class path(object):
    def __init__(self, pathname):
        self._pathname = pathname

    def __str__(self):
        return self._pathname

    def join(self, relpath):
        return self.__class__(os.path.join(self._pathname, relpath))

    def open(self, *a, **kw):
        return file(self._pathname, *a, **kw)
