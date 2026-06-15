"""Constants for Editor launcher."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir

from psiutils.known_paths import resolve_path

# General
AUTHOR = 'Jeff Watkins'
APP_NAME = 'editor'  # must be package name i.e. directory under /src/
APP_AUTHOR = 'psionman'
HTML_DIR = resolve_path('html', __file__)
HELP_URI = ''
EDITOR = 'kate'

# Paths
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), 'config.toml')
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
USER_DATA_FILE = 'data.json'
HOME = str(Path.home())
ICON_DIR = f"{Path(__file__).parent}/icons/"

# GUI
APP_TITLE = 'Editor launcher'
ICON_FILE = Path(
    Path(__file__).parent, 'images', 'file-document-edit-outline.png')
DEFAULT_GEOMETRY = '800x600'
