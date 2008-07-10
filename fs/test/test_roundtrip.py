"""
Unit tests that set up and test operations though the API.

The intent is that you could run these unit tests against
any reasonably normal fs API implementation.
"""

from __future__ import with_statement

from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    ne,
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

    # some implementation might have p1 and p2 be the same object, but
    # that is not required, so identity is not tested in either
    # direction

    def test_eq_positive(self):
        a = self.path.child('foo')
        b = self.path.child('foo')
        eq(a, b)

    def test_eq_negative(self):
        a = self.path.child('foo')
        b = self.path.child('bar')
        assert not a == b, '%r should not equal %r' % (a, b)

    def test_eq_weird(self):
        a = self.path.child('foo')
        b = 'foo'
        assert not a == b, '%r should not equal %r' % (a, b)

    def test_ne_positive(self):
        a = self.path.child('foo')
        b = self.path.child('bar')
        ne(a, b)

    def test_ne_negative(self):
        a = self.path.child('foo')
        b = self.path.child('foo')
        assert not a != b, '%r should be equal to %r' % (a, b)

    def test_ne_weird(self):
        a = self.path.child('foo')
        b = 'foo'
        assert a != b, '%r should not be equal to %r' % (a, b)

    def test_parent(self):
        p = self.path.child('foo')
        c = p.child('bar')
        eq(c.parent(), p)
