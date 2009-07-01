from __future__ import with_statement
import tempfile
import os

from nose.tools import eq_ as eq

from filesystem.test.util import assert_raises, maketemp
    
import filesystem
import filesystem.copyonwrite


def test_iter():
    temp_dir = maketemp()
    temp_files = ['file1', 'file2']
    # put some files in the temporary directory
    for i in temp_files:
        f = open(os.path.join(temp_dir, i), 'w')
        f.close()
    p = filesystem.copyonwrite.path(filesystem.path(temp_dir))
    ## add one more file
    with p.child('file3').open('w') as f:
        f.write('ubba')
    temp_files.append('file3')
    # see whether we actually get the file names with the iterator
    eq(sorted(str(x) for x in p), sorted(str(p.child(x)) for x in temp_files))

def test_not_directory():
    temp_dir = maketemp()
    # prepare a file on which to call the iterator
    f = open(os.path.join(temp_dir, "some_file"), "w")
    f.close()
    # check reaction on getting the iterator
    p = filesystem.copyonwrite.path(filesystem.path(temp_dir).join("some_file"))
    # note: the exception is only raised after calling ``next``
    assert_raises(OSError, list, p)
