from __future__ import with_statement

from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
    maketemp,
    )

import errno
import os

import fs

def test_open_nonexisting():
    p = fs.path(u'/does-not-exist')
    e = assert_raises(IOError, p.open)
    eq(e.errno, errno.ENOENT)

def test_open_reading():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write file with Python's standard API ...
    with file(foo, 'w') as f:
        f.write('bar')
    # ... and read it back with our fs code
    p = fs.path(foo)
    with p.open() as f:
        got = f.read()
    eq(got, 'bar')

def test_open_writing():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write test content
    p = fs.path(foo)
    with p.open('w') as f:
        f.write('bar')
    # read back in and compare
    with file(foo) as f:
        got = f.read()
    eq(got, 'bar')
