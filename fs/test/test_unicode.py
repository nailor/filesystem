from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
   )
    
import fs

def test_path_str_argument():
    p = fs.path("/")
    assert isinstance(str(p), str)
    assert isinstance(unicode(p), unicode)

def test_path_unicode_argument():
    p = fs.path(u"/")
    assert isinstance(str(p), str)
    assert isinstance(unicode(p), unicode)

