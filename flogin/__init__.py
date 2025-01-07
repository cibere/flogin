__title__ = "flogin"
__author__ = "cibere"
__version__ = "2.0.0a"

from .caching import *
from .conditions import *
from .errors import *
from .jsonrpc import *
from .plugin import *
from .query import *
from .search_handler import *
from .settings import *
from .utils import VersionInfo

version_info: VersionInfo = VersionInfo._from_str(__version__)

del VersionInfo
