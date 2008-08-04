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
import fs.copyonwrite

def test_open_nonexisting():
    p = fs.copyonwrite.path(fs.path(u'/does-not-exist'))
    e = assert_raises(IOError, p.open)
    eq(e.errno, errno.ENOENT)

def test_open_for_reading():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write file with Python's standard API ...
    with file(foo, 'w') as f:
        f.write('bar')
    # ... and read it back with our fs code
    p = fs.copyonwrite.path(fs.path(foo))
    with p.open() as f:
        got = f.read()
    eq(got, 'bar')

def test_open_for_writing():
    tmp = maketemp()
    foo = os.path.join(tmp, u'foo')
    # write test content
    p = fs.copyonwrite(fs.path(foo))
    with p.open('w') as f:
        f.write('bar')
        
    # since this is the copy_on_write, the write should not be written
    # to the actual file system
    assert_raises(IOError, file(foo))
