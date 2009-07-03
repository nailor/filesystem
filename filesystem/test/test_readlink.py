
import os
import stat
import errno

from nose.tools import eq_ as eq

from filesystem.test.util import assert_raises, maketemp
import filesystem


def set_up(absolute):
    temp_dir = maketemp()
    os.chdir(temp_dir)
    source_name = os.path.join(temp_dir, "link_source")
    if absolute:
        target_name = os.path.join(temp_dir, "link_target")
    else:
        target_name = "link_target"
    # create the file the link will point to
    f = open(target_name, "w")
    f.close()
    # create link
    os.symlink(target_name, source_name)
    return source_name, target_name

def test_absolute_target():
    source_name, target_name = set_up(absolute=True)
    p = filesystem.path(source_name)
    eq(p.readlink(), target_name)

def test_relative_target():
    source_name, target_name = set_up(absolute=False)
    p = filesystem.path(source_name)
    eq(p.readlink(), target_name)

def test_readlink_on_regular_file():
    source_name, target_name = set_up(absolute=False)
    p = filesystem.path(target_name)
    assert_raises(OSError, p.readlink)

def test_readlink_on_nonexistent_file():
    p = filesystem.path("non-existent-file")
    assert_raises(OSError, p.readlink)
