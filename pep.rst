PEP
===

Motivation
----------

What do we need filefs for?

Rationale
---------

Methods a file system should support
------------------------------------


Mandatory core methods
----------------------

etc.

Random scribblings
------------------

**abstract base class(es)** vs **zope interfaces**

<tobixen> I haven't studied the background much, so I don't know much about the
different philosophies.

<tobixen> we aim for getting into the standard python library, then we
should put more weight on accepted and/or implemented PEPs than
third-part libraries.  At least, we would never get into the standard
library if we depend on zope-code

**"mixin" classes** vs **utility classes**
**sparse API** with only "core" methods vs **dense API** with lots of utility methods

Implementing the dense API is relatively easy, all one needs to do is
to include the appropriate mixins when creating the class.  There is a
performance hit to it, but hardly significant.  The main advantage are
that the API will be trivial to use for the caller.  Arguably, one is
also more free when implementing the file system, i.e. one can choose
whether to implement self.stat() and add a mixin to get self.isdir()
etc implemented - or one can implement self.isdir() etc and let
self.stat() build a return value based on self.isdir(), self.size(),
etc.

Implementing the sparse API is easier and leads to less bloat, but
then one would want to add lots of utility methods in a separated
class.  It makes it more difficult to use the file systems since one
needs more knowledge, i.e. one needs to know where to locate the
utility class, one needs to remember whether a particular method is in
the utility class or directly in the file system, etc.
