from nose.tools import (
    eq_ as eq,
    )

import os
import errno

from filesystem.test.util import (
    maketemp,
    assert_raises,
   )
    
import filesystem

## TODO: move those two tests to a misc test
def test_str_simple():
    p = filesystem.path('/foo')
    got = str(p)
    eq(got, '/foo')

def test_str_root():
    root = filesystem.root
    slash = str(root)
    eq(slash, '/')

def test_str_child_of_root():
    path = filesystem.root.child('tmp')
    eq(str(path), '/tmp')

def test_join_without_slash():
    """
    simple test of joining / and tmp
    """
    path = filesystem.root.join('tmp')
    eq(str(path), '/tmp')

def test_join_with_leading_slash():
    """
    join should raise an exception if one tries to escape from the
    path by giving an absolute path
    """
    e = assert_raises(filesystem.InsecurePathError, filesystem.path('/tmp').join, '/usr')
    eq(str(e), 'path name to join must be relative')

def test_join_with_trailing_slash():
    """
    join should give one slash between each element no matter if
    the parameters are with or without trailing slashes.  join
    should not discard the last trailing slash.
    """
    path = filesystem.root.join('usr/').join('lib').join('python/')
    eq(str(path), "/usr/lib/python/")

def test_join_side_effects():
    """join should return a new object, and not modify the existing"""
    path = filesystem.root
    ret = path.join('tmp')
    eq(str(path), '/')
    assert path is not ret

def test_join_wrong_parameters():
    """join should raise an error if it doesn't get the right parameters"""
    assert_raises(TypeError, filesystem.root.join)
    assert_raises(AttributeError, filesystem.root.join, 32)
    ## TODO: Should or should not join accept multiple arguments?

def test_rename_bad_string():
    tmp = maketemp()
    parent = filesystem.path(tmp)
    old = parent.join('foo')
    assert_raises(
        filesystem.CrossDeviceRenameError,
        old.rename, 'foo')
    eq(filesystem.root, filesystem.root.parent())

def test_parent_at_top():
    eq(filesystem.root, filesystem.root.parent())

def test_parent_of_curdir():
    p = filesystem.path('.')
    eq(p.parent(), p)

def test_parent_of_relative():
    p = filesystem.path('foo')
    eq(p.parent(), filesystem.path('.'))

def test_parent_of_relative_subdir():
    p = filesystem.path('foo/bar')
    eq(p.parent(), filesystem.path('foo'))

def test_name_simple():
    eq(filesystem.path("foo/bar").name(), "bar")

def test_open_nonexisting():
    p = filesystem.path('/does-not-exist')
    e = assert_raises(IOError, p.open)
    eq(e.errno, errno.ENOENT)

def test_open_for_reading():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    # write file with Python's standard API ...
    with open(foo, 'w') as f:
        f.write('bar')
    # ... and read it back with our fs code
    p = filesystem.path(foo)
    with p.open() as f:
        got = f.read()
    eq(got, 'bar')

def test_open_for_writing():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    # write test content
    p = filesystem.path(foo)
    with p.open('w') as f:
        f.write('bar')
    # read back in and compare
    with open(foo) as f:
        got = f.read()
    eq(got, 'bar')
