"""Initialise the application."""

from psiutils.utilities import psi_logger

from filer._version import __version__
from filer.constants import APP_NAME

version = __version__

logger = psi_logger(APP_NAME)
