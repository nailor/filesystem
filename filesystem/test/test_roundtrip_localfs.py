from filesystem.test.util import (
    maketemp,
    )

from filesystem.test import test_roundtrip

import filesystem

class LocalFS_Tests(test_roundtrip.PosixOpMixin):
    def setUp(self):
        self.path = filesystem.path(maketemp())
