#!/usr/bin/python
from setuptools import setup, find_packages
import os

setup(
    name = "filesystem",
    version = "0.2",
    packages = find_packages(),

    author = "Tommi Virtanen",
    author_email = "tv@eagain.net",
    # and others; thank you all

    description = "Pythonic filesystem API",
    long_description = """

A pythonic and flexible filesystem API.

This package implements accessing the local
filesystem, as implemented by your operating
system, and an inmemory filesystem.

Other packages are expected to provide the
same API, for accessing various other things
as files.

""".strip(),
    license = "MIT",
    keywords = "filesystem",
#    url = "http://eagain.net/software/fs/",
    url = "http://eagain.net/gitweb/?p=fs.git",

    classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries
Topic :: System :: Filesystems
Development Status :: 3 - Alpha
""".splitlines(),
# TODO Development Status :: 4 - Beta
# TODO Development Status :: 5 - Production/Stable
    )

