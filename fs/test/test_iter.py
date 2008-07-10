import tempfile
import os

from nose.tools import eq_ as eq

from fs.test.util import maketemp
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
    eq(sorted(str(x) for x in p), sorted(str(p.child(x)) for x in temp_files))
