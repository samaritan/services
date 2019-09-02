import logging
import os

from . import utilities

logger = logging.getLogger(__name__)

_PATH = os.path.abspath(os.path.dirname(__file__))
_PATH = os.path.join(_PATH, 'commands.yml')
COMMANDS = utilities.Yaml.read(_PATH)
