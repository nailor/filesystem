from fs.test.util import (
    maketemp,
    )

from fs.test import test_roundtrip

import fs

class LocalFS_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        self.path = fs.path(maketemp())
