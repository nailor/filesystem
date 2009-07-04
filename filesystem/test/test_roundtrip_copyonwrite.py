import nose

from filesystem.test.util import (
    maketemp,
    )
from filesystem.test import test_roundtrip

import filesystem.copyonwrite
import filesystem

class Copyonwrite_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        real_path = filesystem.path(maketemp())
        self.path = filesystem.copyonwrite.path(real_path)
        assert self.path.exists()

