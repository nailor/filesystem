import tempfile
import os

from nose.tools import eq_ as eq

from fs.test.util import maketemp
import fs


def test_iter():
    temp_dir = maketemp()
    temp_files = ['file1', 'file2', 'file3']

    for i in temp_files:
        f = open(os.path.join(temp_dir, i), 'w')
        f.close()

    p = fs.path(temp_dir)

    eq(sorted([str(i) for i in p]), sorted(temp_files))

