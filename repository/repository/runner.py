import logging
import threading

from . import utilities

logger = logging.getLogger(__name__)


def _exit(process, stream):
    process.wait()
    logger.debug('%s returned %d', process.args, process.returncode)

    error = stream.read()
    if error != '':
        logger.error(error)


class Runner:
    def __init__(self, work_dir):
        self._work_dir = work_dir

    def run(self, command):
        process, ostream, estream = utilities.run(command, self._work_dir)
        thread = threading.Thread(target=_exit, args=(process, estream,))
        thread.start()
        return ostream, thread
