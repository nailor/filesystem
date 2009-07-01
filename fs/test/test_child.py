from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
    )

import fs

def test_new_object():
    p = fs.path(u"/")
    c = p.child(u"segment1", u"segment2")
    assert p is not c
    eq(unicode(p), u"/")
    eq(unicode(c), u"/segment1/segment2")
