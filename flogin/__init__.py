__title__ = "flogin"
__author__ = "cibere"
__version__ = "1.0.0"

from .conditions import *
from .errors import *
from .jsonrpc import *
from .plugin import *
from .query import *
from .search_handler import *
from .settings import *
from .caching import *

from .utils import VersionInfo

version_info: VersionInfo = VersionInfo._from_str(__version__)

del VersionInfo
