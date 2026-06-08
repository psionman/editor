"""Initialise the application."""
from psiutils.utilities import psi_logger
from editor.constants import APP_NAME
from editor._version import __version__

version = __version__

logger = psi_logger(APP_NAME)
