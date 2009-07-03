"""
Implementation of a virtual in-memory file system.  This file system
should not perform any i/o-operations, but it should be possible to
open file-like objects, write to them, and later re-open them with
same pathname and read the contents.
"""
import filesystem
import stat
import posix
import io
import errno
import sys

class _VirtualByteFile(io._BytesIO):
    """
    A BytesIO class that is specialized to be used for the inmem fs.
    """
    ## This class is a wrapper class, the real content is stored in
    ## self._path._file, which we for the convenience copy to
    ## self._path.  Except for self._path and self._file, we keep
    ## self.pos in this wrapper, since that's the only thing that is
    ## different between the different open files.

    ## TODO: implement so that it works with cBytesIO too (ie.
    ## io.BytesIO)
    def __init__(self, path, mode='', *args, **kwargs):
        super().__init__()
        self._buffer = path._file._buffer

        if 'encoding' in kwargs:
            # TODO: Better argument passing is needed, since encoding
            # can be a positional argument
            self._encoding = kwargs['encoding']
        else:
            self._encoding = sys.getdefaultencoding()

        if mode.startswith('w'):
            self.truncate()

        if mode.startswith('a'):
            self.seek(path.size())

class _VirtualTextFile(_VirtualByteFile):
    """
    A text-mode file wrapper class that is specialized to be used for
    the inmem fs.
    """
    def __next__(self):
        return self._btot(super().next())

    def _ttob(self, text):
        """Encode given text to a bytestring using given encoding (or
        platform specific default, if no encoding is given.)
        """
        return bytes(text, self._encoding)

    def _btot(self, bytes):
        return bytes.decode(self._encoding)

    def write(self, text):
        text = self._ttob(text)
        super().write(text)

    def writelines(self, lines):
        lines = (self._ttob(text) for text in lines)
        super().writelines(lines)

    def read(self, size=None):
        return self._btot(super().read(size))

    def readline(self, size=None):
        return self._btot(super().readline(size))

    def readlines(self, sizehint=None):
        return [self._btot(text) for text in super().readlines()]

class path(filesystem.WalkMixin, filesystem.StatWrappersMixin, filesystem.SimpleComparitionMixin):
    """
    An in-memory path.

    In the local file system, the same path can be expressed through
    equal but distinct objects, in this file system we should have
    only one path object for each distinct path (TODO: rename breaks
    with this.  It's the only way to follow the API.  RFC: Should the
    API be changed?).  Creating a new path object is equivalent with
    creating a new distinct file system - the file system has to be
    traversed through .child() or .join()
    """
    def __init__(self, name='', parent=None):
        if '/' in name:
            ## TODO: untested code line
            raise filesystem.InsecurePathError(
                'use child() or join() to traverse the inmem fs')
        
        if parent is None:
            self._parent = self
        else:
            self._parent = parent
        self._name = name
        self._children = {}
        self._stat = ()
        self._file = io._BytesIO()

    def stat(self):
        if not self._stat:
            e = OSError()
            e.errno = errno.ENOENT
            raise e
        if self._file:
            self._stat[6] = len(self._file.getvalue())
        ## bloat ... turning a list to a sequence to a stat_result object ;-)
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
        self._parent._children.pop(self._name)
        self._name = newpath._name
        self._parent = newpath._parent

    def unlink(self):
        if not self.exists():
            e = OSError()
            e.errno = errno.ENOENT
            raise e
        self._file = None
        self._children = {}
        self._stat = ()
        
    remove = unlink

    def rmdir(self):
        if not self.isdir():
            e = OSError()
            e.errno = errno.ENOTDIR
            raise e
        self.unlink()
        
    def join(self, relpath):
        if relpath.startswith('/'):
            raise filesystem.InsecurePathError('path name to join must be relative')
        return self.child(*relpath.split('/'))

    def child(self, segment=None, *segments):
        if not segment:
            return self
        
        if segment not in self._children:
            filesystem.raise_on_insecure_file_name(segment)
            child = self.__class__(name=segment, parent=self)
            self._children[segment] = child
            
        ret = self._children[segment]
        
        if segments:
            return ret.child(*segments)
        else:
            return ret

    def open(self, mode='r', *args, **kwargs):
        if not self.exists():
            self._stat = [stat.S_IFREG + 0o777, 0,0,0,0,0,0,0,0,0]
        if 'b' in mode:
            return _VirtualByteFile(self, mode, *args, **kwargs)
        return _VirtualTextFile(self, mode, *args, **kwargs)
    
    def mkdir(self, may_exist=False, create_parents=False):
        ## TODO: those lines are copied from _localfs.py, consider refactoring
        ## if it's needed in more classes.
        if create_parents and self.parent() is not self:
            self.parent().mkdir(create_parents=True, may_exist=True)
        elif not create_parents:
            if not self.parent().exists():
                err = OSError("parent directory does not exist")
                err.errno = errno.ENOENT
                raise err

        if self._stat:
            if not may_exist or not self.isdir():
                err = OSError()
                err.errno = errno.EEXIST
                raise err
        else:
            self._stat = [stat.S_IFDIR+0o777, 0,0,0,0,0,0,0,0,0]
    
    def __iter__(self):
        if not self.isdir():
            e = OSError()
            if self.isfile():
                e.errno = errno.ENOTDIR
            else:
                e.errno = errno.ENOENT
            raise e
        return [x for x in list(self._children.values()) if x.exists()].__iter__()

root = path()
root.mkdir(may_exist=True, create_parents=True)
path.root = root
