import nose

from filesystem.test.util import (
    maketemp,
    )
from filesystem.test import test_roundtrip

import filesystem.multiplexing
import filesystem

class MultiPlexing_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        self.path = filesystem.multiplexing.path()
        assert not self.path.exists()
        self.path.mkdir(create_parents=True, may_exist=True)
        assert self.path.exists()

class MultiPlexingLocalFS_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        real_path = filesystem.path(maketemp())
        self.path = filesystem.multiplexing.path()
        self.path.bind(real_path)
        assert self.path.exists()


