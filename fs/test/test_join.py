from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
   )
    
import fs

## TODO: move those two tests to a misc test
def test_str_simple():
    p = fs.path(u'/foo')
    got = str(p)
    eq(got, u'/foo')

def test_root():
    root = fs.root
    slash = str(root)
    eq(slash, u'/')

def test_without_slash():
    """
    simple test of joining / and tmp
    """
    path = fs.root.join(u'tmp')
    eq(str(path), u'/tmp')

def test_with_leading_slash():
    """
    join should raise an exception if one tries to escape from the
    path by giving an absolute path
    """
    assert_raises(fs.InsecurePathError, fs.path(u'/tmp').join, u'/usr')

def test_with_trailing_slash():
    """
    join should give one slash between each element no matter if
    the parameters are with or without trailing slashes.  join
    should not discard the last trailing slash.
    """
    path = fs.root.join(u'usr/').join(u'lib').join(u'python/')
    eq(str(path), "/usr/lib/python/")

def test_side_effects():
    """join should return a new object, and not modify the existing"""
    path = fs.root
    ret = path.join(u'tmp')
    eq(str(path), u'/')
    assert path is not ret

def test_wrong_parameters():
    """join should raise an error if it doesn't get the right parameters"""
    assert_raises(TypeError, fs.root.join)
    assert_raises(AttributeError, fs.root.join, 32)
    ## TODO: Should or should not join accept multiple arguments?
