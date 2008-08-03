from fs.test.util import (
    maketemp,
    )
from fs.test import test_roundtrip

import fs.multiplexing
import fs

class MultiPlexing_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        self.path = fs.multiplexing.path()
        assert not self.path.exists()
        self.path.mkdir(create_parents=True, may_exist=True)
        assert self.path.exists()


class MultiPlexingLocalFS_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        real_path = fs.path(maketemp())
        self.path = fs.multiplexing.path()
        self.path.bind(real_path)
        assert self.path.exists()
