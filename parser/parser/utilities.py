import logging
import re

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from .languages import get_languages

_NPATTERN = r'((^|\/)({names}))'
_EPATTERN = r'((\.)({extensions}))'
logger = logging.getLogger(__name__)


def _get_pattern(names, extensions):
    _names = None
    if names is not None:
        _names = (re.escape(i) for i in names)
        _names = _NPATTERN.format(names='|'.join(_names))
    _extensions = None
    if extensions is not None:
        _extensions = (re.escape(i) for i in extensions)
        _extensions = _EPATTERN.format(extensions='|'.join(_extensions))

    if _names is not None and _extensions is not None:
        return '({0}|{1})$'.format(_names, _extensions)
    if _names is not None:
        return '({0})$'.format(_names)
    if extensions is not None:
        return '({0})$'.format(_extensions)
    return None


class Yaml:
    @staticmethod
    def read(path):
        with open(path) as file_:
            return load(file_, Loader=Loader)


class LanguageInferer:
    def __init__(self):
        self._patterns = dict()
        for language, specification in get_languages().items():
            pattern = _get_pattern(**specification)
            logger.debug('Compiled pattern is %s', pattern)
            self._patterns[language] = re.compile(pattern)

    def infer(self, name):
        for language, pattern in self._patterns.items():
            if pattern.search(name):
                return language
        return None
