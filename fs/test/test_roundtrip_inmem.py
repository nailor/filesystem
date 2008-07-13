from fs.test import test_roundtrip

import fs.inmem

class InMem_Tests(test_roundtrip.OperationsMixin):
    def setUp(self):
        self.path = fs.inmem.path()
        assert not self.path.exists()
        self.path.mkdir(create_parents=True, may_exist=True)
        assert self.path.exists()
