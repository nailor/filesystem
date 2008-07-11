from nose.tools import (
    eq_ as eq,
    )

import fs

def test_parent_at_top():
    eq(fs.root, fs.root.parent())

def test_parent_of_curdir():
    p = fs.path('.')
    eq(p.parent(), p)

def test_parent_of_relative():
    p = fs.path('foo')
    eq(p.parent(), fs.path('.'))

def test_parent_of_relative_subdir():
    p = fs.path('foo/bar')
    eq(p.parent(), fs.path('foo'))
