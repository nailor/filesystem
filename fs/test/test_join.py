from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
   )
    
import fs

def test_str_simple():
    p = fs.path(u'/foo')
    got = str(p)
    eq(got, u'/foo')

def test_root():
    root = fs.root
    slash = str(root)
    eq(slash, u'/')

def test_with_slash():
    assert_raises(fs.PathEscapeException, fs.path(u'/tmp').join, u'/usr')

def test_without_slash():
    path = fs.root.join(u'tmp')
    eq(str(path), u'/tmp')
    
def test_side_effects():
    ## join should return a new object, and not modify the existing
    path = fs.root
    ret = path.join(u'tmp')
    eq(str(path), u'/')
    assert path is not ret

