from filesystem._localfs import (
    path,
    root,
    )

## TODO: RFC: is this namespace organization sane?
from filesystem._base import (
    PathnameMixin,
    SimpleComparitionMixin,
    WalkMixin,
    StatWrappersMixin,
    InsecurePathError,
    CrossDeviceRenameError,
    )

