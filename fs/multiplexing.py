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

class path(fs.inmem.path):
    def __init__(self, *args, **kwargs):
        self._bound = None
        super(path, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        if (object.__getattribute__(self, '_bound') and 
            item not in (
                'bind', 'parent', 'unbind', 'child', 'join', 'name') and
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
            

    
root = path()

