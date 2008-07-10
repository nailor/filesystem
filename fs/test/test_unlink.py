from __future__ import with_statement

from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    maketemp,
    assert_raises,
    )

import errno
import os

import fs

def test_unlink():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    with file(foo, 'w') as f:
        f.write('bar')
    fs.path(tmp).child('foo').unlink()
    assert not os.path.exists(foo)

def test_unlink_bad_notfound():
    tmp = maketemp()
    p = fs.path(tmp).child('foo')
    e = assert_raises(
        OSError,
        p.unlink,
        )
    eq(e.errno, errno.ENOENT)

def test_remove():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    with file(foo, 'w') as f:
        f.write('bar')
    fs.path(tmp).child('foo').remove()
    assert not os.path.exists(foo)

def test_remove_bad_notfound():
    tmp = maketemp()
    p = fs.path(tmp).child('foo')
    e = assert_raises(
        OSError,
        p.remove,
        )
    eq(e.errno, errno.ENOENT)
