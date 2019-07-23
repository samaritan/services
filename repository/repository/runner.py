import io
import logging
import threading

from . import cacheable, utilities

logger = logging.getLogger(__name__)


def _exit(process, stream):
    process.wait()
    logger.debug('%s returned %d', process.args, process.returncode)

    error = stream.read()
    if error != '':
        logger.error(error)


class Runner:
    def __init__(self, work_dir, cache):
        self._work_dir = work_dir
        self._cache = cache

    def run(self, command, key=None):
        ostream, thread = None, None
        if key is None:
            ostream, thread = self._run(command, key)
        else:
            if key in self._cache:
                logger.debug('%s IN cache', key)
                ostream = io.StringIO(self._cache.get(key))
            else:
                logger.debug('%s NOT IN cache', key)
                ostream, thread = self._run(command, key)
        return ostream, thread

    def _run(self, command, key):
        process = utilities.run(command, work_dir=self._work_dir)

        args, kwargs = (process.stdout,), dict(errors='replace')
        ostream = None
        if key is not None:
            ostream = cacheable.Cacheable(self._cache, key, *args, **kwargs)
        else:
            ostream = io.TextIOWrapper(*args, **kwargs)
        estream = io.TextIOWrapper(process.stderr, errors='replace')

        thread = threading.Thread(target=_exit, args=(process, estream,))
        thread.start()

        return ostream, thread
