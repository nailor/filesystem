"""
Unit tests that set up and test operations through the API.

The intent is that you could run these unit tests against
any reasonably normal fs API implementation.
"""

from __future__ import with_statement

import nose

from nose.tools import (
    eq_ as eq,
    )

from filesystem.test.util import (
    ne,
    assert_raises
    )

import filesystem

import errno
import stat
import time
import os
import pwd
import grp

class OperationsMixin(object):
    # the actual tests; subclass this and provide a setUp method that
    # gives it a empty self.path for every method

    def _create_file(self, name=u'foo', content='bar'):
        """
        utility function - creates a file and writes some data to it.
        """
        file = self.path.child(name)
        with file.open(u'w') as f:
            f.write(content)

        return file
        

    def test_file(self):
        """
        Test that writes to a file and assert that it's a file and not
        a dir or link.
        """
        # set foo to a path object pointing to a new file with content "bar"
        foo = self._create_file('foo', 'bar')
        # test that the file can be accessed
        p = self.path.child(u'foo')

        assert(p.exists() is True)
        assert(p.isfile() is True)
        assert(p.isdir() is False)

        assert(foo.exists() is True)
        assert(foo.isfile() is True)
        assert(foo.isdir() is False)

        ## TODO: equality is not part of the mandatory API?
        eq(p, foo)
        if hasattr(p, 'islink'):
            assert(p.islink() is False)
            assert(foo.islink() is False)
        if hasattr(p, 'stat'):
            s = p.stat()
            assert(stat.S_ISREG(s.st_mode) is True)
            eq(foo.stat(), p.stat())
    

    def test_stat_missing_file(self):
        p = self.path.child('inexistent_file')
        if hasattr(p, 'stat'):
            e = assert_raises(OSError, p.stat)
            eq(e.errno, errno.ENOENT)
            assert(p.exists() is False)

    def test_join_with_leading_slash(self):
        """
        join with a leading slash should normally throw an
        InsecurePathError - though it may be differently implemented
        from fs to fs.

        Rationale for this test is just to excersise this condition;
        there was a bug in the in-memory fs.
        """
        try:
            self.path.join('/tmp')
        except filesystem.InsecurePathError:
            pass
    
    def test_dir(self):
        """
        Test that takes our testing root dir and asserts it's a dir
        and not a file.  Copied from test_stat.py.
        """
        p = self.path
        assert(p.exists() is True)
        assert(p.isdir() is True)
        assert(p.isfile() is False)
        if hasattr(p, 'islink'):
            assert(p.islink() is False)
        if hasattr(p, 'stat'):
            s = p.stat()
            assert(stat.S_ISDIR(s.st_mode) is True)

    def test_open_read_write(self):
        """
        This will attempt to write to a file and then read the same
        file.  The test also tests that two file handles won't share
        file location, and that the same file can be written to
        several times.
        """
        ## Make sure write-read is repeatable
        for dummy in (0,1):
            p = self._create_file(u'foo', 'barfoo')
            with p.open() as f:
                got = f.read(3)
                eq(got, u'bar')
                
                ## assert that a newly opened file towards same
                ## path starts at the beginning of the file
                with p.open() as f2:
                    got = f2.read(3)
                    eq(got, u'bar')

                ## assert that the previous read on another file
                ## descriptor won't affect the file position of f
                got = f.read(3)
                eq(got, u'foo')
                    
            ## make sure read is repeatable also by accessing the file
            ## by name:
            p = self.path.child(u'foo')
            with p.open() as f:
                got = f.read(3)
                eq(got, u'bar')

    def test_iter(self):
        temp_files = ['file1', 'file2', 'file3']
        # put some files in the temporary directory
        for i in temp_files:
            f = self.path.child(i).open(u'w')
            f.close()
        # see whether we actually get the file names with the iterator
        files = sorted(x.name() for x in self.path)
        eq(files, temp_files)

    def test_not_directory(self):
        # prepare a file on which to call the iterator
        f = self.path.child("some_file").open(u"w")
        f.close()
        # check reaction on getting the iterator
        p = self.path.child("some_file")
        try:
            iterator = iter(p)
            iterator.next()
            assert False ## TODO: better error handling?
        except OSError:
            pass
    
    def test_child_no_segments(self):
        got = self.path.child()
        assert got is self.path

    def test_child_bad_slash(self):
        e = assert_raises(filesystem.InsecurePathError, self.path.child, u'ev/il')
        eq(
            str(e),
            'child name contains directory separator',
            )
        ## Exception should be raised even if it's not evil (?)
        e = assert_raises(filesystem.InsecurePathError, self.path.child, u'notsoevil/')

    def test_child_bad_dotdot(self):
        e = assert_raises(filesystem.InsecurePathError, self.path.child, u'..')
        eq(
            str(e),
            'child trying to climb out of directory',
            )

        ## of course, those should also raise errors
        assert_raises(filesystem.InsecurePathError, self.path.child, u'../')
        assert_raises(filesystem.InsecurePathError, self.path.child, u'..//')
        assert_raises(filesystem.InsecurePathError, self.path.child, u'..//..')

    def test_flush(self):
        """
        Opens two files, writes to one of them, flushes, and asserts
        the content can be read by the other file.
        """
        p = self.path.child(u'foo')
        with p.open(u'w') as fw:
            with p.open() as fr:
                fw.write('barfoo')
                fw.flush()
                got = fr.read(3)
                eq(got, u'bar')

    def test_flush_independent(self):
        p1 = self.path.child(u'foo')
        p2 = self.path.child(u'foo')
        # most often p1 is not p2, but that's not required;
        # however, this test is embarassingly easy for any
        # fs where that is true..
        with p1.open(u'w') as fw:
            with p2.open() as fr:
                fw.write('barfoo')
                if hasattr(fw, 'flush'):
                    fw.flush()
                got = fr.read(3)
                eq(got, u'bar')

    def test_append(self):
        """
        Tests that appending to an existing file works
        """
        p = self.path.child(u'foo')
        with p.open(u'w') as f:
            f.write('foo')
        with p.open(u'a') as f:
            f.write('bar')
        with p.open() as f:
            got = f.read()
            eq(got, 'foobar')

    def test_overwrite(self):
        """
        Tests that appending to an existing file works
        """
        p = self.path.child(u'foo')
        with p.open(u'w') as f:
            f.write('foo')
        with p.open(u'w') as f:
            pass
        with p.open() as f:
            got = f.read()
            eq(got, '')

    # some implementation might have p1 and p2 be the same object, but
    # that is not required, so identity is not tested in either
    # direction

    def test_size(self):
        """
        Test that will write a fixed length byte string to a file,
        close it and check that the file size is correct.
        """
        bytestring = 'abcd' * 128
        eq(len(bytestring), 512)
        p = self.path.child(u'foo')
        with p.open(u'wb') as f:
            f.write(bytestring)
        filesize = p.size()
        eq(filesize, 512)
        if hasattr(p, 'stat'):
            eq(p.stat().st_size, 512)

    def test_size_of_nonexisting_item(self):
        p = self.path.child(u"non-existent-item")
        e = assert_raises(OSError, p.size)
        eq(e.errno, errno.ENOENT)

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
        got = a.rename(b)
        assert got is None, \
            'Rename should not return anything, got: %r' % got
        # a should have mutated to equal b
        eq(a, b)
        # create a new object, just in case a.rename did something
        # weird to b
        c = self.path.child(u'quux')
        eq(a, c)
        with c.open() as f:
            got = f.read()
        eq(got, u'bar')
        assert not self.path.child(u'foo').exists()

    def test_rename_overwrite(self):
        old = self.path.child(u'quux')
        with old.open(u'w') as f:
            f.write('old')
        a = self.path.child(u'foo')
        with a.open(u'w') as f:
            f.write('bar')
        b = self.path.child(u'quux')
        got = a.rename(b)
        assert got is None, \
            'Rename should not return anything, got: %r' % got
        # a should have mutated to equal b
        eq(a, b)
        # create a new object, just in case a.rename did something
        # weird to b
        c = self.path.child(u'quux')
        eq(a, c)
        with c.open() as f:
            got = f.read()
        eq(got, u'bar')

    def test_rename_dir(self):
        a = self.path.child('foo')
        a.mkdir()
        with a.child(u'thud').open(u'w') as f:
            f.write('bar')
        b = self.path.child('quux')
        a.rename(b)
        # create a new object, just in case a.rename did something
        # weird to b
        c = self.path.child(u'quux')
        with c.child('thud').open() as f:
            got = f.read()
        eq(got, u'bar')

    def test_unlink_simple(self):
        a = self._create_file()
        eq(list(self.path), [a])
        a.unlink()
        eq(list(self.path), [])

    def test_unlink_notfound(self):
        p = self.path.child(u'foo')
        e = assert_raises(
            OSError,
            p.unlink,
            )
        eq(e.errno, errno.ENOENT)

    def test_remove_simple(self):
        a = self._create_file()
        eq(list(self.path), [a])
        a.remove()
        eq(list(self.path), [])

    def test_remove_notfound(self):
        p = self.path.child(u'foo')
        e = assert_raises(
            OSError,
            p.remove,
            )
        eq(e.errno, errno.ENOENT)

    def test_mkdir(self):
        eq(list(self.path), [])
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

    def test_mkdir_bad_exists_file(self):
        with self.path.child(u'foo').open('w') as f:
            f.write('FOO')
        e = assert_raises(OSError, self.path.child(u'foo').mkdir)
        eq(e.errno, errno.EEXIST)

    def test_rmdir(self):
        assert self.path.exists()
        p = self.path.child(u'foo')
        assert not p.exists()
        p.mkdir()
        assert p.exists()
        p.rmdir()
        assert not p.exists()
        eq(list(self.path), [])
        # create a new object, just in case .rmdir() stored something
        # in p
        eq(self.path.child(u'foo').exists(), False)

    def test_rmdir_bad_notdir(self):
        p = self._create_file()
        e = assert_raises(
            OSError,
            p.rmdir,
            )
        eq(e.errno, errno.ENOTDIR)

    def test_rmdir_bad_notfound(self):
        p = self.path.child(u'foo')
        e = assert_raises(
            OSError,
            p.rmdir,
            )
        eq(e.errno, errno.ENOENT)

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
            f.write("I'm %s and cloned from test_os.  Blame test_roundtrip.py")
            f.close()

        ## Walk top-down
        all = list(self.path.walk())

        ## all should now be a list of four tuples, one for each
        ## non-empty directory encountered.  It can either be [self.path, SUB1, SUB11, SUB2]
        ## or [self.path, SUB2, SUB1, SUB11].
        ## TODO: refactor this test code, it should check the full return structure
        eq(len(all), 4)
        dir_list = [path_tuple[0].name() for path_tuple in all]
        expected1 = [self.path.name(), 'SUB1', 'SUB11', 'SUB2']
        expected2 = [self.path.name(), 'SUB2', 'SUB1', 'SUB11']
        assert dir_list in (expected1, expected2)

        ## FIRST in the list is self.path.
        ## First element in the self.path-tuple is self.path
        eq(all[0][0], self.path)

        ## Second element is subdirlist - but the ordering is not guaranteed
        subdirs_returned = list(all[0][1])
        subdirs_expected = [sub1_path, sub2_path]
        subdirs_returned.sort()
        subdirs_expected.sort()
        eq(subdirs_returned, subdirs_expected)

        ## third element is the file list
        eq(all[0][2], [tmp1_path])

        ## TODO: the list is not checked completely yet.  Not sure how
        ## to write "clean" test code.  In test_os an attribute
        ## "flipped" is created to indicate the order sub1 and sub2
        ## came out.
        
        ## Prune the search.
        all = []
        for root, dirs, files in self.path.walk():
            all.append((root, dirs, files))
            # Don't descend into SUB1.
            if sub1_path in dirs:
                # Note that this also mutates the dirs we appended to all!
                dirs.remove(sub1_path)
        eq(len(all), 2)
        eq(all[0], (self.path, [sub2_path], [tmp1_path]))
        eq(all[1], (sub2_path, [], [tmp3_path]))

        ## Inject out-of-tree path in dirs
        try:
            for (root, dirs, files) in self.path.walk():
                eq(root, self.path) ## we shouldn't recurse into parent
                dirs[0] = self.path.parent()
        except filesystem.InsecurePathError:
            pass
        

        # Walk bottom-up.
        all = list(self.path.walk(topdown=False))
        eq(len(all), 4)
        dir_list = [path_tuple[0].name() for path_tuple in all]
        expected1 = ['SUB11', 'SUB1', 'SUB2', self.path.name()]
        expected2 = ['SUB2', 'SUB11', 'SUB1', self.path.name()]
        assert dir_list in (expected1, expected2)

        ## TODO: we should do a complete test, just the reverse of
        ## further above - and it should be refactored to avoid
        ## duplicated code.


class LinkOpMixin(OperationsMixin):
    """
    Test suite for file system objects that implements symlinks.

    Subclass this and provide a setUp method that
    gives it a empty self.path for every method
    """
    def test_symlink_readlink_islink(self):
        p = self.path

        ## create a mock file
        src = self._create_file(u'testfile', 'bar')

        ## create a symlink to it
        src.symlink(p.child(u'testlink'))

        ## assert that the link can be read
        ## TODO: readlink seems to return a string instead of a path object
        ## that's probably a bug?
        eq(str(p.child(u'testlink').readlink()), str(p.child(u'testfile')))

        ## assert that the file cannot be read as a link
        assert_raises(OSError, p.child(u'testfile').readlink)

        ## assert that islink works
        assert(p.child(u'testfile').islink() is False)
        assert(p.child(u'testlink').islink() is True)

        ## assert that the link can be opened as a file,
        ## and that we'll get the file content by doing so
        with p.child(u'testlink').open(u'r') as f:
            eq(f.read(3), u'bar')


class PosixOpMixin(LinkOpMixin):
    """
    Mixin that tests all the stuff a posix file system should implement,
    including ordinary file handling, symlinks, etc
    (TODO - not complete)
    """
    def test_methods_exists(self):
        for method in ('stat', 'lstat', 'readlink', 'symlink', 
                       'islink', 'chown'):
            ## TODO: add .... 'chmod', 'lchown', 'access', 'major', 'minor', 'makedev', 'mkfifo', 'mknod', 'utime')
            assert(hasattr(self.path, method))
            assert(hasattr(getattr(self.path, method), '__call__'))

    def _verify_stats(self, stats):
        """common tests from test_stat and test_lstat"""
        ## read mode for user ... is this reasonable to assert?
        assert(stats.st_mode & 0400)
        
        
        ## testing st_ino and st_dev - they should exist
        stats.st_ino
        stats.st_dev
        
        ## number of hard links to this inode
        eq(stats.st_nlink, 1)
        
        ## ownership should match our efficient uid
        eq(stats.st_uid, os.geteuid())
        ## don't assume too much about the gid through
        stats.st_gid

        ## this assert is a bit unstable - of course the clock can be
        ## modified while we're running tests, or we could be paused
        ## or running pdb or whatever ... but 12 seconds ought to be
        ## sufficient.
        assert(time.time()-stats.st_mtime<12)
        assert(time.time()-stats.st_ctime<12)
        ## is this a sane assert?
        eq(stats.st_mtime, stats.st_ctime)

        ## I wouldn't like to add sleeps into the test ... 
        ## but we ought to test whether st_mtime, st_ctime and st_atime is
        ## updated correctly.  Well, let's do that in the utime test ...

        ## the stat should be available both as a dict and a list.  I
        ## think the positions and number of elements are fixed in the
        ## standard.
        eq(len(stats), 10)
        eq(stats[0], stats.st_mode)
        eq(stats[6], stats.st_size)

    def test_stat(self):
        ## create a file to play with
        file = self._create_file(u'stat_test_file')
        stats = file.stat()

        ## testing st_mode
        assert(stat.S_ISREG(stats.st_mode))
        assert(file.isfile())

        ## size should be 3
        eq(stats.st_size, file.size())
        eq(stats.st_size, 3)
        
        ## for a non-link, lstat and stat should yield same result
        eq(stats, file.lstat())

        self._verify_stats(stats)
        
    def test_lstat(self):
        link = self.path.child(u'stat_test_link')
        self.path.child(u'doesnexist').symlink(link)
        lstats = link.lstat()
        assert(stat.S_ISLNK(lstats.st_mode))
        ## assert a "sane" size (is this sane?)
        assert(lstats.st_size>0 and lstats.st_size<1024)
        
        self._verify_stats(lstats)

        assert_raises(OSError, link.stat)

    def test_chown_lchown_1(self):
        ## create a file and a link
        file = self._create_file(u'chown_test_file1')
        link = self.path.child('chown_test_link1')
        file.symlink(link)

        ## chown should accept both numeric and string arguments
        ## ... batteries included!
        ## gid is optional

        ## should pass without problems, changing nothing
        ## (assuming group ownership is the same for the file and the link)
        for chown in (file.chown, file.lchown, link.chown, link.lchown):
            chown(os.geteuid())
            chown(os.getlogin())
            chown(new_group=file.stat().st_gid)
            chown(new_group=grp.getgrgid(file.stat().st_gid).gr_name)
            chown(os.geteuid(), file.stat().st_gid)
            chown(os.getlogin(), grp.getgrgid(file.stat().st_gid).gr_name)

    def test_chown_lchown_root(self):
        ## this test has some requirements ...
        if os.geteuid():
            raise nose.SkipTest("this test can only be run as root ... :/")

        try:
            pwd.getpwnam('nobody')
        except KeyError:
            raise nose.SkipTest("this test relies on user nobody to exist")

        ## setup - create a file and a link
        file = self._create_file(u'chown_test_file1')
        link = self.path.child('chown_test_link1')
        file.symlink(link)

        ## Hm ... TODO: fix this neater, copy logics from the test_chown_lchown_group test
        link.lchown(0)
        link.chown('nobody')
        eq(file.stat().st_uid, pwd.getpwnam('nobody').pw_uid)
        eq(link.stat().st_uid, pwd.getpwnam('nobody').pw_uid)
        eq(link.lstat().st_uid, 0)
        link.chown(0)
        eq(file.stat().st_uid, 0)
        file.chown('nobody')
        eq(file.stat().st_uid, pwd.getpwnam('nobody').pw_uid)
        file.chown(0)
        eq(file.stat().st_uid, 0)
        link.lchown('nobody')
        eq(file.stat().st_uid, 0)
        eq(link.stat().st_uid, 0)
        eq(link.lstat().st_uid, pwd.getpwnam('nobody').pw_uid)

    def test_chown_lchown_group(self):
        """user should be able to change group of file/link"""
        
        ## setup part 1, find two user group ids we can use
        gids = os.getgroups()
        if len(gids)<2:
            raise SkipTest("need to be member of at least two groups to run this test")
        ## setup, part 2 - create a file and a link
        file = self._create_file(u'chown_test_file1')
        link = self.path.child('chown_test_link1')
        file.symlink(link)

        ## helper function - check that file has gid0 and link has
        ## gid1 or opposite
        def _chk_grps(reverse=0):
            eq(file.stat().st_gid, gids[reverse])
            eq(link.stat().st_gid, gids[reverse])
            eq(link.lstat().st_gid, gids[not reverse])

        uid = os.geteuid()

        ## setting file to gid0 and link to gid1
        file.lchown(uid, gids[0])
        link.lchown(uid, gids[1])
        _chk_grps()
        ## reversing
        file.chown(uid, gids[1])
        link.lchown(uid, gids[0])
        _chk_grps(1)
        ## setting link to gid0 and file to gid1
        link.chown(uid, gids[0])
        link.lchown(uid, gids[1])
        _chk_grps(0)


    def test_chown_lchown_raises_error(self):
        ## create a file and a link
        file = self._create_file(u'chown_test_file1')
        link = self.path.child('chown_test_link1')
        file.symlink(link)

        if not os.geteuid():
            raise nose.SkipTest("this test can not be run as root")

        ## should give permission denied
        assert_raises(OSError, file.chown, 0)
        assert_raises(OSError, file.lchown, 0)

    ## TODO: write tests for all the other posix-required methods...

