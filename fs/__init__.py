from fs._localfs import (
    path,
    root,
    )

## TODO: RFC: is this namespace organization sane?
from fs._base import (
    PathnameMixin,
    SimpleComparitionMixin,
    WalkMixin,
    StatWrappersMixin,
    InsecurePathError,
    CrossDeviceRenameError,
    )

