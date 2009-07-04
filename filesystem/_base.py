import os
import stat
import errno

class InsecurePathError(Exception):
    """
    The path operation is unsafe to perform.

    An insecure operation was requested, for example:

     * a join is performed with an absolute path as input parameter
     * '..' is passed as a parameter to child method
     * Symlinks not passing security validations
    """
    pass


class CrossDeviceRenameError(Exception):
    """
    Rename old and new paths are not on the same filesystem.

    Rename cannot work across different python filesystems backends.
    New path is not on the local filesystem.
    """
    pass

## utility function for checking for safe file names.
## TODO: should it be encapsulated within a class?
def raise_on_insecure_file_name(name):
    if u'/' in name:
        raise InsecurePathError(
            'child name contains directory separator')
    # this may be too naive
    if name == u'..':
        raise InsecurePathError(
            'child trying to climb out of directory')



## TODO: RFC: Is there any presedence for this naming convention?  As
## I understand it, "Mixin" means that this class can be mixed into
## the parent class list in a class definition to get misc methods
## mixed in - but I find this naming convention mostly confusing.  I
## think "...Helper" is clearer?  2008-07-12
class StatWrappersMixin(object):
    """
    If a class implements stat(), several other methods can be
    implemented as wrappers around stat.  Simply pull in this class to
    get those implemented: exists, isdir, isfile, islink, size.  (islink
    depends on lstat being implemented - assumes the file system does
    not support symlinks and hence has no symlinks if lstat is not
    implemented)
    """
    def size(self):
        """
        Return the size of the item represented by this path.

        If the path cannot be accessed, raise an ``OSError``.
        """
        return self.stat().st_size

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
        return (hasattr(self, 'lstat') and 
                stat.S_ISLNK(self.lstat().st_mode))


class WalkMixin(object):
    """
    This class gives the method walk.  If there is no
    filesystem-specific way to do a walk, and if your file system
    class implements iteration, parent, isdir and islink, it may
    inheritate this class.
    """
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
            if (d.parent() != self or d == self):
                raise InsecurePathError("walk is only allowed into subdirs")
            if not (hasattr(d, 'islink') and d.islink()):
                for w in d.walk(topdown):
                    yield w
        if not topdown:
            yield (self, subdirs, nondirs)

    

class PathnameMixin(object):
    """
    This class asserts self._pathname exists
    
    Class for dealing with pathnames, to be subclassed by file system
    implementations where such path name handling is useful.

    This class implements comparition operators, it allows pathname
    building through the join and child methods, and one can move
    upwards in the hierarchy by using the parent method.

    No methods in this class will perform any IO-operations, though
    the class depends on the os-module to actually do some of the
    work.
    """
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

            p = filesystem.path(u"/some/path").join(u"some_more")

        The appended path has to be a relative path. Otherwise, an
        ``InsecurePathError`` is raised.
        """
        if relpath.startswith(u'/'):
            raise InsecurePathError('path name to join must be relative')
        return self.__class__(os.path.join(self._pathname, relpath))


    def child(self, *segments):
        """
        Return a child of the ``path`` object. (A child is a path
        representing a path one or more levels "deeper" than the
        original path, on which this method is called.)

        This method takes one or more positional arguments,
        ``segments``, each representing an item further below the
        path.

        For example:

            >>> path = filesystem.path(u"/usr/share")
            >>> child_path = path.child(u"doc", u"python")
            >>> print child_path
            /usr/share/doc/python

        If one of the segments contains a slash or equals the string
        "..", that is considered an insecure operation and thus an
        ``InsecurePathError`` is raised.
        """
        p = self
        for segment in segments:
            raise_on_insecure_file_name(segment)
            p = p.join(segment)
        return p

    def parent(self):
        """
        Return a path object representing the parent of this ``path``
        object on which this method is called. The result is the path
        one level up.
        """
        if self._pathname=='/':
            return self
        head, tail = os.path.split(self._pathname)
        if head == '':
            head = '.'
        return self.__class__(head)

    def name(self):
        """Return last segment of path."""
        return os.path.basename(self._pathname)

    def _incomparable(self, other):
        """
        Returns ``NotImplemented`` if the other object is considered
        incomparable, and ``False`` if the other object is considered
        comparable.  Can be used like:
        
            return (self._incomparable(other) or
                    other._pathname == self._pathname)
        """
        ## TODO: trap: we're asserting that root wasn't replaced with
        ## a equivalent but non-identical root object (comparing
        ## other.root != self.root would cause a recursion)
        if not hasattr(other, 'root') or other.root is not self.root:
            return NotImplemented
        if not isinstance(other, PathnameMixin):
            return NotImplemented
        return False

    def __cmp__(self, other):
        return (self._incomparable(other) or
                cmp(self._pathname, other._pathname))
    
class SimpleComparitionMixin(object):
    """
    This class implements the equity/comparition-methods using
    self.name() and self.parent().  Not compatible with the
    PathnameMixin class.
    """
    def _incomparable(self, other):
        """
        Returns ``NotImplemented`` if the other object is considered
        incomparable, and ``False`` if the other object is considered
        comparable.  Can be used like:
        
            return (self._incomparable(other) or
                    other._pathname == self._pathname)
        """
        for name in ('root', 'parent', 'name'):
            if not hasattr(other, name):
                return NotImplemented
        return False

    def __cmp__(self, other):
        if self._incomparable(other):
            return NotImplemented

        ## root object
        if self.parent() is self and other.parent() is other:
            return cmp(self.name(), other.name())
        
        ## compare parents ... and if they are equal, compare name
        return (cmp(self.parent(), other.parent()) or
                  cmp(self.name(), other.name()))

    def __unicode__(self):
        if self.parent() == self:
            return u'/'
        return str(self.parent())+ u'/' + self.name()

    def __str__(self):
        return unicode(self).encode('utf8')

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))
