"""
Implementation of a virtual in-memory file system.  This file system
should not perform any i/o-operations, but it should be possible to
open file-like objects, write to them, and later re-open them with
same pathname and read the contents.
"""
import fs
import stat
import posix
import StringIO
import errno

class _VirtualFile(StringIO.StringIO):
    """
    A StringIO class that is specialized to be used for the inmem fs.
    """
    def __init__(self, path, content=''):
        self._path = path
        path._files.add(self)
        return StringIO.StringIO.__init__(self, content)

    def flush(self):
        content = self.getvalue()
        self._path._content = content
        ## Update other files.  Hm.  This will break.
        #for f in self._path._files:
            #f.truncate()
            #f.write(content)
        
    def close(self):
        self.flush()
        self._path._files.remove(self)

    def __exit__(self, a, b, c):
        return self.close()
    
    def __enter__(self):
        return self

class path(fs.WalkMixin, fs.StatWrappersMixin, fs.SimpleComparitionMixin):
    def __init__(self, name='/', parent=None):
        if parent is None:
            self._parent = self
        else:
            self._parent = parent
        self._name = name
        self._children = {}
        self._stat = ()
        self._files = set()
        self._content = ""

    def stat(self):
        if not self._stat:
            e = OSError()
            e.errno = errno.ENOENT
            raise e
        return self._stat

    def parent(self):
        return self._parent

    def name(self):
        return self._name

    def rename(self, newpath):
        newpath.parent().mkdir(may_exist=True, create_parents=True)
        newpath._files = self._files
        newpath._content = self._content
        newpath._children = self._children
        newpath._stat = self._stat
        self._files = None
        self._content = ""
        self._children = {}
        self._stat = ()
        return newpath

    def unlink(self):
        self._file = None
        self._children = {}
        self._stat = ()
        
    remove = unlink
    rmdir = remove

    def join(self, relpath):
        if relpath.startswith(u'/'):
            raise InsecurePathError('path name to join must be relative')
        return self.child(*relpath.split('/'))

    def child(self, segment, *segments):
        if not self._children.has_key(segment):
            child = self.__class__(segment, self)
            self._children[segment] = child
            
        ret = self._children[segment]
        
        if segments:
            return ret.child(*segments)
        else:
            return ret

    def open(self, mode=u'rw'):
        if not self.exists():
            self._stat = posix.stat_result((stat.S_IFREG + 0777, 0,0,0,0,0,0,0,0,0))
        return _VirtualFile(self, self._content)
    
    def mkdir(self, may_exist=False, create_parents=False):
        ## TODO: those lines are copied from _localfs.py, consider refactoring
        ## if it's needed in more classes.
        if create_parents and self.parent() is not self:
            self.parent().mkdir(create_parents=True, may_exist=True)
        elif not create_parents:
            if not self.parent().exists():
                err = OSError()
                err.errno = errno.ENOENT
                raise err

        if self._stat:
            if not may_exist or not self.isdir():
                err = OSError()
                err.errno = errno.EEXIST
                raise err
        else:
            self._stat = posix.stat_result((stat.S_IFDIR+0777, 0,0,0,0,0,0,0,0,0))
    
    def __iter__(self):
        return [x for x in self._children.values() if x.exists()].__iter__()

root = path()
root.mkdir(may_exist=True, create_parents=True)
path.root = root
