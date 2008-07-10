import tempfile
import os

from nose.tools import eq_ as eq

from fs.test.util import assert_raises, maketemp
    
import fs


def test_iter():
    temp_dir = maketemp()
    temp_files = ['file1', 'file2', 'file3']
    # put some files in the temporary directory
    for i in temp_files:
        f = open(os.path.join(temp_dir, i), 'w')
        f.close()
    # see whether we actually get the file names with the iterator
    p = fs.path(temp_dir)
    eq(sorted([str(i) for i in p]), sorted(temp_files))

def test_not_directory():
    temp_dir = maketemp()
    # prepare a file on which to call the iterator
    f = open(os.path.join(temp_dir, "some_file"), "w")
    f.close()
    # check reaction on getting the iterator
    p = fs.path(temp_dir).join("some_file")
    iterator = iter(p)
    # note: the exception is only raised after calling ``next``
    assert_raises(OSError, iterator.next)
