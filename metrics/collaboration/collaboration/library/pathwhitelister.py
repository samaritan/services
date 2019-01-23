import logging
import re

logger = logging.getLogger(__name__)

_NPATTERN = r'((^|\/)({names}))'
_EPATTERN = r'((\.)({extensions}))'

def _get_pattern(names, extensions):
    _names = None
    if names is not None:
        _names = _NPATTERN.format(names='|'.join(names))
    _extensions = None
    if extensions is not None:
        _extensions = _EPATTERN.format(extensions='|'.join(extensions))

    if _names is not None and _extensions is not None:
        return '({0}|{1})$'.format(_names, _extensions)
    if _names is not None:
        return '({0})$'.format(_names)
    if extensions is not None:
        return '({0})$'.format(_extensions)
    return None


class PathWhitelister:
    def __init__(self, names, extensions):
        self.names = names
        self.extensions = extensions

        self._re = None
        self._compile_re()

    def is_valid(self, path):
        return True if self._re is None else self._re.search(path) is not None

    def _compile_re(self):
        pattern = _get_pattern(self.names, self.extensions)
        logger.debug('Compiled pattern is "%s"', pattern)
        if pattern is not None:
            self._re = re.compile(pattern, flags=re.IGNORECASE)
