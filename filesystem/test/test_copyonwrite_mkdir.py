

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

def test_mkdir():
    tmp = maketemp()
    filesystem.copyonwrite.path(filesystem.path(tmp)).child('foo').mkdir()
    foo = os.path.join(tmp, 'foo')
    assert not os.path.isdir(foo)

def test_mkdir_bad_exists():
    tmp = maketemp()
    p = filesystem.copyonwrite.path(filesystem.path(tmp)).child('foo')
    with p.open('w') as f:
        f.write('bar')
    e = assert_raises(
        OSError,
        p.mkdir,
        )
    eq(e.errno, errno.EEXIST)
