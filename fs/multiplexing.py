"""
Simple filesystem based on the in-memory file system.

Through the method "bind", one can introduce a new subfilesystem,
i.e.:
    fs.multiplexing.path('/mnt/ftp.python.org').bind(
        fs.ftpfs.path(host='ftp.python.org'))

TODO: more test code and more documentation
"""

import fs
import fs.inmem

def _has_common_ancestor(self, other):
    ## TODO RFC: maybe make this a method of all the filesystem
    ## classes?
    ## TODO: may probably be optimized.
    prev = None
    trail = []
    while prev is not other:
        trail.append(other)
        prev = other
        other = other.parent()
    while not self in trail:
        p = self.parent()
        if p == self:
            return False
        self = self.parent()
    return self


class path(fs.inmem.path):
    def __init__(self, *args, **kwargs):
        self._bound = None
        super(path, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        if (object.__getattribute__(self, '_bound') and 
            item not in (
                'bind', 'parent', 'unbind', 'child',
                'join', 'name', 'rename', 'walk') and
            not item.startswith('_')):
            return getattr(object.__getattribute__(self, '_bound'), item)
        else:
            return object.__getattribute__(self, item)

    def bind(self, path):
        self._bound = path

    def unbind(self):
        self._bound = False

    def child(self, segment=None, *segments):
        if not segment:
            return self
        childnode = super(path, self).child(segment)
        assert hasattr(self, '_bound')
        if self._bound and childnode._bound is None:
            childnode._bound = self._bound.child(segment)
        return childnode.child(*segments)

    def rename(self, new_path):
        """
        At least those scenarioes should be covered:
        
         * both self and new_path are unbound multiplexing paths, all
           up to a common ancestor.
         
         * self is a bound multiplexing path, and new_path is either a
           multiplexing path with same kind of bounding object and
           some common parent.

         * self is a bound multiplexing path, and new_path is a path
           of the bounding type, having some common parent with
           self._bound.

        TODO: As for now, I'm just aiming for the tests to pass.
        Probably need to refine and rethink what rename means for a
        multiplexing file system.  Probably we should check more
        careful that all conditions match and throw errors.
        """
        if not self._bound and (
            not hasattr(new_path, '_bound') or not new_path._bound):
            if not _has_common_ancestor(self, new_path):
                raise fs.CrossDeviceRenameError()
            return super(path, self).rename(new_path)

        if self._bound and hasattr(new_path, '_bound') and new_path._bound:
            ancestor = _has_common_ancestor(self, new_path)
            if not ancestor:
                raise fs.CrossDeviceRenameError()
            real_ancestor = _has_common_ancestor(self._bound, new_path._bound)
            if not real_ancestor:
                raise fs.CrossDeviceRenameError()
            if ancestor._bound <> real_ancestor:
                raise fs.CrossDeviceRenameError()
            
            ## TODO: all children are corrupt, since they are bound to
            ## localfs objects with wrong pathnames.  Deleting the
            ## link to them won't really solve the problem, since
            ## there may still be other references to them.  We
            ## probably need to go through all children objects and
            ## rebind.  But first I'll need to create a test to prove
            ## it's broken.
            self._children = {}
            self._bound.rename(new_path._bound)
            return super(path, self).rename(new_path)

        raise fs.CrossDeviceRenameError()

    
root = path()

