import errno
import os
import stat

from filesystem._base import (
    PathnameMixin,
    WalkMixin,
    StatWrappersMixin,
    InsecurePathError,
    CrossDeviceRenameError,
    )

class path(PathnameMixin, WalkMixin, StatWrappersMixin):
    ## RFC: do we need a chroot method?
    
    def open(self, *args, **kwargs):
        """
        Return a file-like object denoted by this path object.

        Arguments of the ``open`` call are passed to Python's ``file``
        constructor. If that raises an exception it will be passed on
        to the caller of the ``open`` method.
        """
        return open(self._pathname, *args, **kwargs)

    def __iter__(self):
        """
        Return an iterator over this ``path`` object, assuming it
        denotes a directory.

        If the list of files in the directory can't be determined or
        the supposed directory isn't a directory at all, raise an
        ``OSError``.
        """
        for item in os.listdir(self._pathname):
            yield self.child(item)

    def rename(self, new_path):
        """
        Rename this path a new path ``new_path`` (a ``path`` object).
        The object is changed in-place.

        If the renaming operation fails, raise an ``OSError``.
        """
        ## TODO: RFC: I think we should support passing new_path as a string
        ## TODO: RFC: when we implement wrapping of OSError / IOError,
        ## this code should probably be refactored.
        if not hasattr(new_path, 'root') or self.root != new_path.root:
            raise CrossDeviceRenameError()
        try:
            os.rename(self._pathname, new_path._pathname)
        except OSError, e:
            if e.errno == errno.EXDEV:
                raise CrossDeviceRenameError()
            else:
                raise
        self._pathname = new_path._pathname

    def stat(self):
        """
        Return the status information for this ``path`` object. The
        return value is of the same type as for ``os.stat``.
        """
        return os.stat(self._pathname)

    def lstat(self):
        return os.lstat(self._pathname)

    def symlink(self, target):
        """
        let self become a symlink to target
        """
        if not hasattr(target, 'root') or self.root != target.root:
            raise OSError(errno=errno.EXDEV)
        os.symlink(self._pathname, target._pathname)

    def readlink(self):
        """
        Return the ``path`` as a string to which the link represented
        by this ``path`` object points. If this ``path`` object
        doesn't represent a link, raise an ``OSError``.

        If the operation fails, also raise an ``OSError`` exception.
        """
        # TODO: do we care about ``os.readlink`` returning a string or
        # unicode string?
        ## TODO: shouldn't we return a path object instead?
        return os.readlink(self._pathname)


    def unlink(self):
        """
        Remove the file or link identified by this path.

        If the item cannot be removed, raise an ``OSError``.
        """
        os.unlink(self._pathname)

    remove = unlink

    def mkdir(self, may_exist=False, create_parents=False):
        """
        Creates the path.  may_exists will ignore dir exists
        exceptions
        """
        ## TODO: logics to handle create_parents is already copied into inmem.py
        ## Consider refactoring out if it's needed in more classes.
        if create_parents:
            if self.parent() == self:
                return
            self.parent().mkdir(create_parents=True, may_exist=True)
            
        try:
            os.mkdir(self._pathname)
        except OSError, e:
            if may_exist and e.errno == errno.EEXIST:
                pass
            else:
                raise

    def rmdir(self):
        os.rmdir(self._pathname)

root = path(u'/')
## RFC: I want every path for every file system to have a root object for identification purposes.
path.root = root
