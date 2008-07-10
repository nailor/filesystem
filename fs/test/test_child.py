from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
    )

import fs

def test_simple():
    path = fs.root.child(u'tmp')
    eq(str(path), u'/tmp')

def test_no_segments():
    got = fs.root.child()
    assert got is fs.root

def test_bad_slash():
    e = assert_raises(fs.InsecurePathError, fs.root.child, u'ev/il')
    eq(
        str(e),
        'child name contains directory separator',
        )

    ## Exception should be raised even if it's not evil (?)
    e = assert_raises(fs.InsecurePathError, fs.root.child, u'notsoevil/')

def test_bad_dotdot():
    e = assert_raises(fs.InsecurePathError, fs.root.child, u'..')
    eq(
        str(e),
        'child trying to climb out of directory',
        )

    ## of course, those should also raise errors
    assert_raises(fs.InsecurePathError, fs.root.child, u'../')
    assert_raises(fs.InsecurePathError, fs.root.child, u'..//')
    assert_raises(fs.InsecurePathError, fs.root.child, u'..//..')
