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
    assert_raises
    )

import errno

class OperationsMixin(object):
    # the actual tests; subclass this and provide a setUp method that
    # gives it a empty self.path for every method

    def test_open_read_write(self):
        p = self.path.child(u'foo')
        with p.open(u'w') as f:
            f.write('bar')
        with p.open() as f:
            got = f.read()
        eq(got, u'bar')

    # some implementation might have p1 and p2 be the same object, but
    # that is not required, so identity is not tested in either
    # direction

    def test_eq_positive(self):
        a = self.path.child(u'foo')
        b = self.path.child(u'foo')
        eq(a, b)

    def test_eq_negative(self):
        a = self.path.child(u'foo')
        b = self.path.child(u'bar')
        assert not a == b, u'%r should not equal %r' % (a, b)

    def test_eq_weird(self):
        a = self.path.child(u'foo')
        b = u'foo'
        assert not a == b, u'%r should not equal %r' % (a, b)

    def test_ne_positive(self):
        a = self.path.child(u'foo')
        b = self.path.child(u'bar')
        ne(a, b)

    def test_ne_negative(self):
        a = self.path.child(u'foo')
        b = self.path.child(u'foo')
        assert not a != b, u'%r should be equal to %r' % (a, b)

    def test_ne_weird(self):
        a = self.path.child(u'foo')
        b = u'foo'
        assert a != b, u'%r should not be equal to %r' % (a, b)

    def test_lt_positive(self):
        assert self.path.child(u'a') < self.path.child(u'b')

    def test_lt_negative(self):
        assert not self.path.child(u'b') < self.path.child(u'a')

    def test_lt_negative_equal(self):
        assert not self.path.child(u'a') < self.path.child(u'a')

    def test_le_positive(self):
        assert self.path.child(u'a') <= self.path.child(u'b')

    def test_le_positive_equal(self):
        assert self.path.child(u'a') <= self.path.child(u'a')

    def test_le_negative(self):
        assert not self.path.child(u'b') <= self.path.child(u'a')

    def test_gt_positive(self):
        assert self.path.child(u'b') > self.path.child(u'a')

    def test_gt_negative(self):
        assert not self.path.child(u'a') > self.path.child(u'b')

    def test_gt_negative_equal(self):
        assert not self.path.child(u'a') > self.path.child(u'a')

    def test_ge_positive(self):
        assert self.path.child(u'b') >= self.path.child(u'a')

    def test_ge_positive_equal(self):
        assert self.path.child(u'a') >= self.path.child(u'a')

    def test_ge_negative(self):
        assert not self.path.child(u'a') >= self.path.child(u'b')

    def test_parent(self):
        p = self.path.child(u'foo')
        c = p.child(u'bar')
        eq(c.parent(), p)

    def test_rename_simple(self):
        a = self.path.child(u'foo')
        with a.open(u'w') as f:
            f.write('bar')
        b = self.path.child(u'quux')
        a.rename(b)
        # create a new object, just in case a.rename did something
        # weird to b
        c = self.path.child(u'quux')
        eq(a, c)
        with c.open() as f:
            got = f.read()
        eq(got, u'bar')

    def test_rename_overwrite(self):
        old = self.path.child(u'quux')
        with old.open(u'w') as f:
            f.write('old')
        a = self.path.child(u'foo')
        with a.open(u'w') as f:
            f.write('bar')
        b = self.path.child(u'quux')
        a.rename(b)
        # create a new object, just in case a.rename did something
        # weird to b
        c = self.path.child(u'quux')
        eq(a, c)
        with c.open() as f:
            got = f.read()
        eq(got, u'bar')

    def test_unlink_simple(self):
        a = self.path.child(u'foo')
        with a.open(u'w') as f:
            f.write('bar')
        a.unlink()
        eq(list(self.path), [])

    def test_remove_simple(self):
        a = self.path.child(u'foo')
        with a.open(u'w') as f:
            f.write('bar')
        a.remove()
        eq(list(self.path), [])

    def test_mkdir(self):
        self.path.child(u'foo').mkdir()
        eq(list(self.path), [self.path.child(u'foo')])
        # create a new object, just in case .mkdir() stored something
        # in p
        eq(self.path.child(u'foo').isdir(), True)

        ## if the dir already exists, an error should be raised
        e = assert_raises(OSError, self.path.child(u'foo').mkdir)
        eq(e.errno, errno.EEXIST)


        ## but one can ask for this error not to be raised
        p = self.path.child(u'foo').mkdir(may_exist=True)

        ## mkdir will raise errors if the parent dirs doesnu't exist
        e = assert_raises(
            OSError, self.path.join(u'newdir/subdir1/subdir2').mkdir)
        eq(e.errno, errno.ENOENT)

        ## but one can ask for this error not to be raised
        self.path.join(u'newdir/subdir1/subdir2').mkdir(create_parents=True)
        eq(self.path.join(u'newdir/subdir1/subdir2').isdir(), True)

    def test_rmdir(self):
        p = self.path.child(u'foo')
        p.mkdir()
        p.rmdir()
        eq(list(self.path), [])
        # create a new object, just in case .rmdir() stored something
        # in p
        eq(self.path.child(u'foo').exists(), False)

    def test_walk(self):
        ## File tree copied from /usr/lib/python2.5/test/test_os.py, class WalkTests
        sub1_path = self.path.join(u"SUB1")
        sub11_path = sub1_path.join(u"SUB11")
        sub2_path = self.path.join(u"SUB2")
        tmp1_path = self.path.join(u"tmp1")
        tmp2_path = sub1_path.join(u"tmp2")
        tmp3_path = sub2_path.join(u"tmp3")

        ## Create dirs
        sub11_path.mkdir(may_exist=True, create_parents=True)
        sub2_path.mkdir(may_exist=True, create_parents=True)

        ## First test, walk on an empty dir should return a list with one item
        empty_dir_walk = list(sub11_path.walk())
        eq(len(empty_dir_walk), 1)
        ## Each list item is a three-element tuple just like with os.path:
        ## (directory, subdirlist, filelist)
        eq(empty_dir_walk[0][0], sub11_path)
        eq(empty_dir_walk[0][1], [])
        eq(empty_dir_walk[0][2], [])

        ## Create some files
        for path in tmp1_path, tmp2_path, tmp3_path:
            f = path.open(u'w')
            f.write(u"I'm %s and cloned from test_os.  Blame test_roundtrip.py")
            f.close()

        ## Walk top-down
        all = list(self.path.walk())
        
        ## all should now be a list of four tuples, one for each
        ## non-empty directory encountered.  It can either be [self.path, SUB1, SUB11, SUB2]
        ## or [self.path, SUB2, SUB1, SUB11].
        eq(len(all), 4)
        dir_list = [path_tuple[0].name() for path_tuple in all]
        expected1 = [self.path.name(), 'SUB1', 'SUB11', 'SUB2']
        expected2 = [self.path.name(), 'SUB2', 'SUB1', 'SUB11']
        assert dir_list in (expected1, expected2)
        
        ## TODO: more test code: test the top-down attribute, test
        ## in-place editing of the subdirectories list, test that one
        ## cannot escape from the directory tree by in-place editing
        ## of the subdirectories list.  TODO: think about error
        ## handling
        
        
