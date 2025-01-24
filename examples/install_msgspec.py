# Libraries that need to be compiled (like msgspec) due to C extensions or other reasons
# Don't work very well with the way flow requires you to package your plugin
# Plus, flow doesn't ship with pip. Because of this, `flogin.Pip` is provided
# As a way to install packages through pip in a production environment when
# pip might not exist.

# This example ensures that the msgspec package is properly installed before attempting to import it

from pathlib import Path

from flogin import Pip

# import flogin.utils.print to allow us to print to logs
# and import setup_logging so we can get the logs from
# Pip and our prints
from flogin.utils import print, setup_logging

setup_logging()

# The default libs dir for the Pip class is `lib`, but you can specify different as shown below.
# Please ensure that the path exists BEFORE adding it to path, otherwise imports won't work properly.
# Because of this, `Pip` will raise an error if the dir doesn't exist.

libs_dir = Path("lib")

with Pip(libs_dir) as pip:
    if pip.ensure_installed("msgspec"):
        print("Reinstalled msgspec")
    else:
        print("msgspec already installed")


# Reimport flogin as a way to seperate what is setup and what is the plugin.
# This line right here is a good place to split your runner file and your plugin's files

import msgspec

from flogin import Plugin, Query

plugin = Plugin()


@plugin.search()
async def s(query: Query):
    return f"{msgspec!r}"


# Since we setup logging earlier, tell our plugin not to set it up again
plugin.run(setup_default_log_handler=False)
