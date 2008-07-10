import os
import stat


class InsecurePathError(Exception):
    """
    The path operation is unsafe to perform.

    An insecure operation was requested, for example:

     * a join is performed with an absolute path as input parameter
     * '..' is passed as a parameter to child method
     * Symlinks not passing security validations
    """
    pass


class NoDirectoryError(Exception):
    """
    Raised if an iterator is requested on a path that doesn't
    represent a directory.
    """
    pass


class CrossdeviceRenameError(Exception):
    """
    Rename old and new paths are not on the same filesystem.

    Rename cannot work across different python filesystems backends.
    New path is not on the local filesystem.
    """
    pass


class path(object):
    def __init__(self, pathname):
        self._pathname = pathname

    def __str__(self):
        return str(self._pathname)

    def __unicode__(self):
        return unicode(self._pathname)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._pathname)

    def join(self, relpath):
        """
        Return a new ``path`` object, with the relative path
        ``relpath`` joined on it.

        For example,

            p = fs.path(u"/some/path").join(u"some_more")

        The appended path has to be a relative path. Otherwise,
        an ``InsecurePathError`` is raised. 
        """
        if relpath.startswith(u'/'):
            raise InsecurePathError('path name to join must be relative')
        return self.__class__(os.path.join(self._pathname, relpath))

    def open(self, *args, **kwargs):
        """
        Return a file-like object denoted by this path object.

        Arguments of the ``open`` call are passed to Python's
        ``file`` constructor. If that raises an exception it will
        be passed on to the caller of the ``open`` method.
        """
        return open(self._pathname, *args, **kwargs)

    def __iter__(self):
        """
        Return an iterator over this ``path`` object, assuming
        it denotes a directory.

        If the list of files in the directory can't be determined
        or the supposed directory isn't a directory at all, raise
        an ``OSError``.
        """
        for item in os.listdir(self._pathname):
            yield self.child(item)

    def child(self, *segments):
        p = self
        for segment in segments:
            if u'/' in segment:
                raise InsecurePathError(
                      'child name contains directory separator')
            # this may be too naive
            if segment == u'..':
                raise InsecurePathError(
                      'child trying to climb out of directory')
            p = p.join(segment)
        return p

    def parent(self):
        head, tail = os.path.split(self._pathname)
        return self.__class__(head)

    def name(self):
        """Return last segment of path"""
        return os.path.basename(self._pathname)


    def __eq__(self, other):
        if not isinstance(other, path):
            return NotImplemented
        return self._pathname == other._pathname

    def __ne__(self, other):
        if not isinstance(other, path):
            return NotImplemented
        return self._pathname != other._pathname

    def __lt__(self, other):
        if not isinstance(other, path):
            return NotImplemented
        return self._pathname < other._pathname

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        if not isinstance(other, path):
            return NotImplemented
        return self._pathname > other._pathname

    def __ge__(self, other):
        return self > other or self == other

    def rename(self, newpath):
        """
        Rename this path. Mutates the object.
        """
        if not isinstance(newpath, path):
            raise CrossdeviceRenameError()
        os.rename(self._pathname, newpath._pathname)
        self._pathname = newpath._pathname

    def stat(self):
        return os.stat(self._pathname)

    def isdir(self):
        return stat.S_ISDIR(self.stat().st_mode)

    def isfile(self):
        return stat.S_ISREG(self.stat().st_mode)

    def islink(self):
        return stat.S_ISLNK(self.stat().st_mode)

    def size(self):
        return self.stat().st_size

    def unlink(self):
        os.unlink(self._pathname)

    remove = unlink

    def mkdir(self):
        os.mkdir(self._pathname)

