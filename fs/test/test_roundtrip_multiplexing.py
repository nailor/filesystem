from fs.test import test_roundtrip

import fs.multiplexing

class MultiPlexing_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        self.path = fs.multiplexing.path()
        assert not self.path.exists()
        self.path.mkdir(create_parents=True, may_exist=True)
        assert self.path.exists()
