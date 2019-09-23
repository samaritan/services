import io
import logging
import threading

from . import utilities

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, path):
        self._path = path

    def archive(self, sha, path):
        command = f'git archive --format=zip --output={path}/{sha}.zip {sha}'
        return f'{path}/{sha}.zip' if self._run(command) == 0 else None

    def _run(self, command):
        def _exit(process, stream):
            process.wait()
            logger.debug('%s returned %d', process.args, process.returncode)

            error = stream.read()
            if error != '':
                logger.error(error)
            return process.returncode

        process = utilities.run(command, work_dir=self._path)
        estream = io.TextIOWrapper(process.stderr, errors='replace')

        thread = threading.Thread(target=_exit, args=(process, estream,))
        thread.start()
        thread.join()

        return process.returncode
