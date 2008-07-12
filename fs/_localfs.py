import errno
import os
import stat

from fs._base import (
    PathnameMixin,
    InsecurePathError,
    CrossDeviceRenameError)

class path(PathnameMixin):
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
        ## TODO: I think we should support passing new_path as a string
        
        ## TODO: We need to catch the equivalent error from os.rename
        ## as well.  -- tobixen, 2008-07-12
        if not hasattr(new_path, 'root') or self.root != new_path.root:
            raise CrossDeviceRenameError()
        os.rename(self._pathname, new_path._pathname)
        self._pathname = new_path._pathname

    def stat(self):
        """
        Return the status information for this ``path`` object. The
        return value is of the same type as for ``os.stat``.
        """
        return os.stat(self._pathname)

    def exists(self):
        """
        Return ``True`` if this path actually exists in the concrete
        filesystem, else return ``False``.

        If there is an error, raise ``OSError``. Note that the
        non-existence of the path isn't an error, but simply returns
        ``False``.
        """
        try:
            self.stat()
        except OSError, e:
            # ENOENT means the path wasn't found
            if e.errno == errno.ENOENT:
                return False
            else:
                raise
        return True

    def isdir(self):
        """
        Return ``True`` if the path corresponds to a directory or a
        symlink to one, else return ``False``.

        Raise an ``OSError`` if the operation fails.
        """
        return stat.S_ISDIR(self.stat().st_mode)

    def isfile(self):
        """
        Return ``True`` if the path corresponds to a file or a symlink
        to it, else return ``False``.

        Raise an ``OSError`` if the operation fails.
        """
        return stat.S_ISREG(self.stat().st_mode)

    def islink(self):
        """
        Return ``True`` if the path corresponds to a symlink, else
        return ``False``.

        Raise an ``OSError`` if the operation fails.
        """
        return stat.S_ISLNK(self.stat().st_mode)

    def readlink(self):
        """
        Return the ``path`` as a string to which the link represented
        by this ``path`` object points. If this ``path`` object
        doesn't represent a link, raise an ``OSError``.

        If the operation fails, also raise an ``OSError`` exception.
        """
        # TODO: do we care about ``os.readlink`` returning a string or
        # unicode string?
        return os.readlink(self._pathname)

    def size(self):
        """
        Return the size of the item represented by this path.

        If the path cannot be accessed, raise an ``OSError``.
        """
        return self.stat().st_size

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

    def walk(self, topdown=True):
        """Directory tree generator.

        For each directory in the directory tree rooted at top
        (including top itself), yields a 3-tuple

          (directory, subdirectories, nondirs)

        When topdown is true, the caller can modify the subdirectories
        list in-place (e.g., via del or slice assignment), and walk
        will only recurse into the remaining subdirectories.  This can
        be used to prune the search, or to impose a specific order of
        visiting.

        TODO: os.walk can handle errors through callbacks, not to
        interrupt the whole walk on errors.  We should probably do the
        same.

        TODO: we should have a follow_symlinks flag, but then we also
        need loop control.
        """
        children = list(self)
        ## TODO: optimize?
        subdirs = [c for c in children if c.isdir()]
        nondirs = [c for c in children if not c.isdir()]
        if topdown:
            yield (self, subdirs, nondirs)
        for d in subdirs:
            if (d.parent() != self):
                raise InsecurePathError("walk is only allowed into subdirs")
            if not d.islink():
                for w in d.walk(topdown):
                    yield w
        if not topdown:
            yield (self, subdirs, nondirs)

root = path(u'/')
## RFC: I want every path for every file system to have a root object for identification purposes.
path.root = root
