import tempfile
import os

import util
import fs


def create_temp_files(dir, amount=5):
    return [tempfile.mkstemp(dir=dir) for i in range(amount)]


def test_iter():
    try:
        temp_dir = util.maketemp()
        temp_files = create_temp_files(temp_dir)

        p = fs.path(temp_dir)

        assert(i in temp_files for i in p)
        assert(len(list(p)) == len(temp_files))
    finally:
        # Delete files
        for i in temp_files:
            os.close(i[0])
            os.unlink(i[1])
        os.rmdir(temp_dir)

