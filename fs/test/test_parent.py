from nose.tools import (
    eq_ as eq,
    )

import fs

def test_parent_at_top():
    eq(fs.root, fs.root.parent())
