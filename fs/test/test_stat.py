from __future__ import with_statement
import os
import stat
import errno

from nose.tools import eq_ as eq

from fs.test.util import assert_raises, maketemp
import fs


def test_stat_isdir():
    temp_dir = maketemp()
    p = fs.path(temp_dir)
    s = p.stat()
    assert(stat.S_ISDIR(s.st_mode) is True)

def test_stat_isreg():
    # set up
    temp_dir = maketemp()
    foo = os.path.join(temp_dir, u'foo')
    with open(foo, 'w') as f:
        f.write('bar')
    # test
    p = fs.path(foo)
    s = p.stat()
    assert(stat.S_ISREG(s.st_mode) is True)

def test_stat_exists_missing():
    temp_dir = maketemp()
    p = fs.path(temp_dir).child('foo')
    assert(p.exists() is False)

def test_stat_missing_file():
    temp_dir = maketemp()
    p = fs.path(os.path.join(temp_dir, 'inexistent_file'))
    e = assert_raises(OSError, p.stat)
    eq(e.errno, errno.ENOENT)

## TODO: I think the following two tests can be removed, as they are
## almost duplicated in the roundtrip test?
def test_dir():
    temp_dir = maketemp()
    p = fs.path(temp_dir)
    assert(p.exists() is True)
    assert(p.isdir() is True)
    assert(p.isfile() is False)
    assert(p.islink() is False)

def test_file():
    # set up
    temp_dir = maketemp()
    foo = os.path.join(temp_dir, u'foo')
    with open(foo, 'w') as f:
        f.write('bar')
    # test
    p = fs.path(foo)
    assert(p.exists() is True)
    assert(p.isfile() is True)
    assert(p.isdir() is False)
    assert(p.islink() is False)

## test_size moved to the roundtrip test
