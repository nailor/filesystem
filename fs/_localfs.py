import os

class InsecurePathError(Exception):
    """
    The path operation is unsafe to perform.

    An insecure operation was requested, for example:

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
            raise InsecurePathError('path name to join must be relative')
        return self.__class__(os.path.join(self._pathname, relpath))

    def open(self, *a, **kw):
        return file(self._pathname, *a, **kw)

    def __iter__(self):
        for i in os.listdir(self._pathname):
            yield path(i)

    def child(self, *segments):
        p = self
        for segment in segments:

            if '/' in segment:
                raise InsecurePathError('child name contains directory separator')

            # this may be too naive
            if segment == '..':
                raise InsecurePathError('child trying to climb out of directory')

            p = p.join(segment)
        return p
