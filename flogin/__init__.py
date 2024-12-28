__title__ = "flogin"
__author__ = "cibere"
__version__ = "1.0.0"


from typing import Literal, NamedTuple

from .conditions import *
from .errors import *
from .jsonrpc import *
from .plugin import *
from .query import *
from .search_handler import *
from .settings import *
from .caching import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]


version_info: VersionInfo = VersionInfo(major=0, minor=1, micro=0, releaselevel="beta")

del NamedTuple, Literal, VersionInfo
