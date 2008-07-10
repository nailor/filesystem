from __future__ import with_statement
import os
import stat

from nose.tools import eq_ as eq

from fs.test.util import assert_raises, maketemp
import fs


def test_stat_isdir():
    temp_dir = maketemp()

    p = fs.path(temp_dir)
    s = p.stat()
    assert(stat.S_ISDIR(s.st_mode))


def test_stat_isreg():
    temp_dir = maketemp()
    foo = os.path.join(temp_dir, u'foo')
    with open(foo, 'w') as f:
        f.write('bar')

    p = fs.path(foo)
    s = p.stat()
    assert(stat.S_ISREG(s.st_mode))


def test_stat_missing_file():
    temp_dir = maketemp()
    p = fs.path(os.path.join(temp_dir, 'inexistent_file'))
    assert_raises(OSError, p.stat)


def test_stat_size():
    temp_dir = maketemp()
    s = 'bar'
    foo = os.path.join(temp_dir, u'foo')
    with open(foo, 'w') as f:
        f.write(s)

    p = fs.path(foo)
    eq(p.stat().st_size, len(s))

