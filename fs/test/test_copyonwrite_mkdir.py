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
import fs.copyonwrite

def test_mkdir():
    tmp = maketemp()
    fs.copyonwrite.path(fs.path(tmp)).child('foo').mkdir()
    foo = os.path.join(tmp, 'foo')
    assert not os.path.isdir(foo)

def test_mkdir_bad_exists():
    tmp = maketemp()
    p = fs.copyonwrite.path(fs.path(tmp)).child('foo')
    with p.open('w') as f:
        f.write('bar')
    e = assert_raises(
        OSError,
        p.mkdir,
        )
    eq(e.errno, errno.EEXIST)
