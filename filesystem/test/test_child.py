from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    assert_raises,
    )

import filesystem

def test_new_object():
    p = filesystem.path("/")
    c = p.child("segment1", "segment2")
    assert p is not c
    eq(str(p), "/")
    eq(str(c), "/segment1/segment2")
