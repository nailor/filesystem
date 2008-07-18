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
    ## This class is a wrapper class, the real content is stored in
    ## self._path._file, which we for the convenience copy to
    ## self._path.  Except for self._path and self._file, we keep
    ## self.pos in this wrapper, since that's the only thing that is
    ## different between the different open files.
    def __init__(self, path, mode=u''):
        ## we'll have to use __dict__ here to get around __setattr__
        self.__dict__['_path'] = path
        self.__dict__['_file'] = path._file
        self.__dict__['pos'] = 0
        
        if mode.startswith(u'w'):
            self.truncate()

        if mode.startswith(u'a'):
            self.seek(self.len)

    def __getattr__(self, item):
        return getattr(self._file, item)

    def __setattr__(self, item, newvalue):
        if item == 'pos':
            self.__dict__[item] = newvalue
        else:
            return setattr(self._file, item, newvalue)

    def __exit__(self, a, b, c):
        pass

    def close(self):
        pass
    
    def __enter__(self):
        return self

class path(fs.WalkMixin, fs.StatWrappersMixin, fs.SimpleComparitionMixin):
    """
    An in-memory path.

    In the local file system, the same path can be expressed through
    equal but distinct objects, in this file system we have only one
    path object for each distinct path.  Creating a new path object is
    equivalent with creating a new distinct file system - the file
    system has to be traversed through .child() or .join()
    """
    def __init__(self, name='', parent=None):
        if u'/' in name:
            raise InsecurePathError(
                'use child() or join() to traverse the inmem fs')
        
        if parent is None:
            self._parent = self
        else:
            self._parent = parent
        self._name = name
        self._children = {}
        self._stat = ()
        self._file = StringIO.StringIO()

    #def __eq__(self, other):
        ## as said above, two equal paths should always be same object.
        #return self is other

    def stat(self):
        if not self._stat:
            e = OSError()
            e.errno = errno.ENOENT
            raise e
        if self._file:
            self._stat[6] = self._file.len
        ## bloat ... turning a list to a sequence to a stat_result object ;-)
        ## Well, StringIO implementation is not quite optimal anyway ;-)
        return posix.stat_result(list(self._stat))

    def parent(self):
        return self._parent

    def name(self):
        return self._name

    def rename(self, newpath):
        newpath.parent().mkdir(may_exist=True, create_parents=True)
        newpath._file = self._file
        newpath._children = self._children
        newpath._stat = self._stat
        self._name = newpath._name
        self._parent = newpath._parent

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

    def open(self, mode=u'r', *args, **kwargs):
        if not self.exists():
            self._stat = [stat.S_IFREG + 0777, 0,0,0,0,0,0,0,0,0]
        return _VirtualFile(self, mode)
    
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
            self._stat = [stat.S_IFDIR+0777, 0,0,0,0,0,0,0,0,0]
    
    def __iter__(self):
        return [x for x in self._children.values() if x.exists()].__iter__()

root = path()
root.mkdir(may_exist=True, create_parents=True)
path.root = root
