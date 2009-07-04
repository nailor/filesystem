PEP: XXX
Title: File System API Library
Version: $Revision$
Last-Modified: $Date$
Author: Tobias Brox <tobixen@gmail.com>
Status: Draft
Type: Library
Content-Type: text/x-rst
Created: 03-Jul-2009
Post-History: Not posted yet

Abstract
========

This PEP provides a standard API for accessing file system objects.
The reference implementation gives access to a local file system using
the API, as well as access to several other "file system-like
objects".

This document is work in progress.

Rationale
=========

The current API for accessing the file system is scattered all over the place, built-ins and miscellaneous stdlib:

  * file(), open(), file objects
  * os.listdir(), os.walk()
  * os.path.exists(), os.chdir()
  * os.unlink(), os.rename()
  * stat, mmap

Error handling is done through two exception classes, OSError and
IOError, and one needs to inspect a POSIX error number to find the
error.

The current API is ugly and non-intuitive, difficult to mock up in
tests, and too specific to the local file system.  There is clearly a
need for a more elegant approach, because there are already several
projects partly or fully implementing "file system objects".  It would
clearly be better to have one standard library included in the python
distribution.

With a common API, one could pass around different file system objects
- this allows non-native file systems and meta file systems to be
used, i.e. pointers into tarballs, access to remote file systems
i.e. through ssh/sftp, copy-on-write file systems, in-memory file
systems, test-specific file systems designed to fail, file systems
owith non-native permission systems, chroot-jailed file systems, etc.

Usage
=====

Typical example for writing to a temp file:

::
    from filesystem import path
    

Mandatory Methods for a Path Object
===================================

name 
    gives the name of a file, typically the last segment of a full
    path name.

child, join, parent
    for navigating the directory tree

open 
    returns a file-like object

__iter__
    yields a list of objects in a directory

walk 
    for walking through a tree - more or less equivalent with os.walk

remove, unlink
    deleting an object.  The two methods are equivalent.  Cannot be
    used on subdirectories.
    
rename
    renaming or moving an object.

mkdir, rmdir
    creating/removing subdirectories.

exists, isdir, isfile 
    testing for object existance and type    

size
    returns size of a file, measured in number of bytes


Non-Mandatory Methods
=====================

Some methods only makes sense for some file systems, other methods are
considered "feature creep".  Still, someone will most likely want to
create filesystems with those features, so this PEP contains
API recommendations for future file systems.

Those methods are not mandatory, but implemented for the default file
system in the reference implementation:

* stat, lstat
* readlink, symlink, islink
* chown, chmod, lchown
* access
* major, minor
* makedev, mkfifo, mknod
* utime
* others?

Those methods could arguably be useful to have in an "batteries
included" file system object, and may be included in some of the file
systems supported in the reference distribution.

* copy
* mktemp/tempnam/tmpfile
* deletetree
* move (as rename, but should work across different file systems)

Reference Implementation
========================

Available at http://eagain.net/gitweb/?p=fs.git or git://eagain.net/fs.git

Copyright
=========

This document has been placed in the public domain.


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:
