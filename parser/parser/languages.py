import logging
import os

from . import utilities

logger = logging.getLogger(__name__)

_PATH = os.path.abspath(os.path.dirname(__file__))

def get_languages():
    return utilities.Yaml.read(os.path.join(_PATH, 'languages.yml'))
