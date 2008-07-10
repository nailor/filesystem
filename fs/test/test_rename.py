from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    maketemp,
    assert_raises,
    )

import fs

def test_rename_bad_string():
    tmp = maketemp()
    parent = fs.path(tmp)
    old = parent.join(u'foo')
    assert_raises(
        fs.CrossdeviceRenameError,
        old.rename, 'foo')
    eq(fs.root, fs.root.parent())
