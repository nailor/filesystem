from nose.tools import (
    eq_ as eq,
    )

import fs

def test_name_simple():
    eq(fs.path("foo/bar").name(), "bar")
