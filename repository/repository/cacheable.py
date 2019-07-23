import io
import logging

logger = logging.getLogger(__name__)


class Cacheable(io.TextIOWrapper):
    def __init__(self, cache, key, *args, **kwargs):
        self._cache = cache
        self._key = key

        self._data = list()
        super().__init__(*args, **kwargs)

    def readline(self, size=-1):
        line = super().readline(size)
        if line == '':  # Stream is at EOF
            self._persist()
        else:
            self._data.append(line)
        return line

    def _persist(self):
        self._cache.set(self._key, ''.join(self._data))
        logger.debug('%s cached', self._key)
