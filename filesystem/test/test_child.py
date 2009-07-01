from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    assert_raises,
    )

import filesystem

def test_new_object():
    p = filesystem.path(u"/")
    c = p.child(u"segment1", u"segment2")
    assert p is not c
    eq(unicode(p), u"/")
    eq(unicode(c), u"/segment1/segment2")
