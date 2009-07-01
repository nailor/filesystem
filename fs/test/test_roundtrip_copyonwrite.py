import nose

from fs.test.util import (
    maketemp,
    )
from fs.test import test_roundtrip

import fs.copyonwrite
import fs

class Copyonwrite_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        real_path = fs.path(maketemp())
        self.path = fs.copyonwrite.path(real_path)
        assert self.path.exists()

    def test_child_bad_slash(self):
        raise nose.SkipTest('TODO temporary pardon')
