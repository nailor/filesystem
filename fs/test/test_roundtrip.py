"""
Unit tests that set up and test operations though the API.

The intent is that you could run these unit tests against
any reasonably normal fs API implementation.
"""

from __future__ import with_statement

from nose.tools import (
    eq_ as eq,
    )

class OperationsMixin(object):
    # the actual tests; subclass this and provide a setUp method that
    # gives it a empty self.path for every method

    def test_open_read_write(self):
        p = self.path.child('foo')
        with p.open('w') as f:
            f.write('bar')
        with p.open() as f:
            got = f.read()
        eq(got, 'bar')
