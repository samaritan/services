import io
import logging
import os
import shlex
import subprocess

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


logger = logging.getLogger(__name__)


def quote(text):
    return shlex.quote(text)


def run(command, work_dir=None):
    work_dir = os.path.realpath(work_dir) if work_dir is not None else work_dir

    logger.debug(command)
    process = subprocess.Popen(
        command, cwd=work_dir, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    ostream = io.TextIOWrapper(process.stdout, errors='replace')
    estream = io.TextIOWrapper(process.stderr, errors='replace')

    return process, ostream, estream


class Yaml:
    @staticmethod
    def read(path):
        with open(path) as file_:
            return load(file_, Loader=Loader)
