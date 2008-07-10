import os

class PathEscapeException(Exception):
    """
    Should be raised on those occations:
     * a join is performed with an absolute path as input parameter
     * '..' is passed as a parameter to child method
     * Symlinks not passing security validations
    """
    pass

class path(object):
    def __init__(self, pathname):
        self._pathname = pathname

    def __str__(self):
        return self._pathname

    def join(self, relpath):
        if relpath.startswith('/'):
            raise PathEscapeException
        return self.__class__(os.path.join(self._pathname, relpath))

    def open(self, *a, **kw):
        return file(self._pathname, *a, **kw)

    def __iter__(self):
        return iter(os.listdir(self._pathname))

