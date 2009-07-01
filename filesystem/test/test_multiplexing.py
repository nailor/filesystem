import filesystem.multiplexing 
import filesystem

from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    ne,
    maketemp,
    )

from filesystem.test.util import (
    maketemp,
    )

def test_bind():
    """
    Testing the multiplexing file system (TODO: split up into multiple tests, clean up)
    """
    mp_root = filesystem.multiplexing.path()
    mountpoint = mp_root.join('mnt/tmp/')
    real_pathname = maketemp()
    mountpoint.bind(filesystem.path(real_pathname))
    real_path = filesystem.path(real_pathname)
    
    ## TODO: RFC: I'm not sure whether it should pass or not since the
    ## parent differs.
    #eq(real_path, mountpoint)
    #eq(mountpoint, real_path)
    ne(real_path, mountpoint)
    ne(mountpoint, real_path)

    ## mountpoint.parent should give the parent node in the multiplexing fs
    ## real_path.parent should give the real parent directory
    ne(mountpoint.parent(), real_path.parent())
    assert mountpoint.isdir()
    assert real_path.isdir()

    ## Let's make a subdirectory under our "mounted" directory
    foo = mp_root.join('mnt/tmp/foo')
    foo2 = mountpoint.child('foo')
    real_foo = real_path.child('foo')
    ## same directory, same parent
    eq(foo, foo2)
    ## same directory, different parents
    #eq(foo, real_foo)
    ne(foo, real_foo)
    assert not foo.exists()
    assert not foo2.exists()
    assert not real_foo.exists()
    foo.mkdir()
    assert foo.isdir()
    assert foo2.isdir()
    assert real_foo.isdir()
    ## same directory, different parent
    #eq(real_foo, foo2)
    ne(real_foo, foo2)
    
    
