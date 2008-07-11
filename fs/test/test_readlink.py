from __future__ import with_statement
import os
import stat
import errno

from nose.tools import eq_ as eq

from fs.test.util import assert_raises, maketemp
import fs


def set_up(absolute):
    temp_dir = maketemp()
    source_name = os.path.join(temp_dir, u"link_source")
    if absolute:
        target_name = os.path.join(temp_dir, u"link_target")
    else:
        target_name = u"link_target"
    # create the file the link will point to
    f = open(target_name, "w")
    f.close()
    # create link
    os.symlink(target_name, source_name)
    return source_name, target_name

def test_absolute_target():
    source_name, target_name = set_up(absolute=True)
    p = fs.path(source_name)
    eq(p.readlink(), target_name)

def test_relative_target():
    source_name, target_name = set_up(absolute=False)
    p = fs.path(source_name)
    eq(p.readlink(), target_name)

