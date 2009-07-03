# encoding: utf-8

from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    assert_raises,
   )
    
import filesystem

def test_path_str_argument():
    p = filesystem.path("/")
    assert isinstance(str(p), str)
    assert isinstance(str(p), str)

def test_path_unicode_argument():
    p = filesystem.path("/")
    assert isinstance(str(p), str)
    assert isinstance(str(p), str)

def test_repr():
    p = filesystem.path("/test\xe4")
    assert isinstance(repr(p), str)

