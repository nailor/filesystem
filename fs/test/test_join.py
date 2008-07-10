from nose.tools import (
    eq_ as eq,
    )

import fs

def test_str_simple():
    p = fs.path('/foo')
    got = str(p)
    eq(got, '/foo')

def test_root():
    root = fs.root
    slash = str(root)
    eq(slash, '/')

def test_join():
    path = fs.root.join('/tmp')
    eq(str(path), '/tmp')
    
