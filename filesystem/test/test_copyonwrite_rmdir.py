

from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    maketemp,
    assert_raises,
    )

import errno
import os

import filesystem
import filesystem.copyonwrite

def test_rmdir():
    tmp = maketemp()
    foo = os.path.join(tmp, 'foo')
    os.mkdir(foo)
    filesystem.copyonwrite.path(filesystem.path(tmp)).child('foo').rmdir()
    assert os.path.exists(foo)

def test_rmdir_bad_notdir():
    tmp = maketemp()
    p = filesystem.copyonwrite.path(filesystem.path(tmp)).child('foo')
    with p.open('w') as f:
        f.write('bar')
    e = assert_raises(
        OSError,
        p.rmdir,
        )
    eq(e.errno, errno.ENOTDIR)

def test_rmdir_bad_notfound():
    tmp = maketemp()
    p = filesystem.copyonwrite.path(filesystem.path(tmp)).child('foo')
    e = assert_raises(
        OSError,
        p.rmdir,
        )
    eq(e.errno, errno.ENOENT)
