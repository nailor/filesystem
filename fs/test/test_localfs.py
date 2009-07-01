from nose.tools import (
    eq_ as eq,
    )

import os
import errno

from fs.test.util import (
    maketemp,
    assert_raises,
   )
    
import fs

## TODO: move those two tests to a misc test
def test_str_simple():
    p = fs.path(u'/foo')
    got = str(p)
    eq(got, u'/foo')

def test_str_root():
    root = fs.root
    slash = str(root)
    eq(slash, u'/')

def test_str_child_of_root():
    path = fs.root.child(u'tmp')
    eq(str(path), u'/tmp')

def test_join_without_slash():
    """
    simple test of joining / and tmp
    """
    path = fs.root.join(u'tmp')
    eq(str(path), u'/tmp')

def test_join_with_leading_slash():
    """
    join should raise an exception if one tries to escape from the
    path by giving an absolute path
    """
    e = assert_raises(fs.InsecurePathError, fs.path(u'/tmp').join, u'/usr')
    eq(str(e), 'path name to join must be relative')

def test_join_with_trailing_slash():
    """
    join should give one slash between each element no matter if
    the parameters are with or without trailing slashes.  join
    should not discard the last trailing slash.
    """
    path = fs.root.join(u'usr/').join(u'lib').join(u'python/')
    eq(str(path), "/usr/lib/python/")

def test_join_side_effects():
    """join should return a new object, and not modify the existing"""
    path = fs.root
    ret = path.join(u'tmp')
    eq(str(path), u'/')
    assert path is not ret

def test_join_wrong_parameters():
    """join should raise an error if it doesn't get the right parameters"""
    assert_raises(TypeError, fs.root.join)
    assert_raises(AttributeError, fs.root.join, 32)
    ## TODO: Should or should not join accept multiple arguments?

def test_rename_bad_string():
    tmp = maketemp()
    parent = fs.path(tmp)
    old = parent.join(u'foo')
    assert_raises(
        fs.CrossDeviceRenameError,
        old.rename, 'foo')
    eq(fs.root, fs.root.parent())

def test_parent_at_top():
    eq(fs.root, fs.root.parent())

def test_parent_of_curdir():
    p = fs.path('.')
    eq(p.parent(), p)

def test_parent_of_relative():
    p = fs.path('foo')
    eq(p.parent(), fs.path('.'))

def test_parent_of_relative_subdir():
    p = fs.path('foo/bar')
    eq(p.parent(), fs.path('foo'))

def test_name_simple():
    eq(fs.path("foo/bar").name(), "bar")

def test_open_nonexisting():
    p = fs.path(u'/does-not-exist')
    e = assert_raises(IOError, p.open)
    eq(e.errno, errno.ENOENT)

def test_open_for_reading():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write file with Python's standard API ...
    with file(foo, 'w') as f:
        f.write('bar')
    # ... and read it back with our fs code
    p = fs.path(foo)
    with p.open() as f:
        got = f.read()
    eq(got, 'bar')

def test_open_for_writing():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write test content
    p = fs.path(foo)
    with p.open('w') as f:
        f.write('bar')
    # read back in and compare
    with file(foo) as f:
        got = f.read()
    eq(got, 'bar')
