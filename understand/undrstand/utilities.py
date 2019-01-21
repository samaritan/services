import logging
import os
import shlex
import subprocess


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
    (out, err) = [x.decode(errors='replace') for x in process.communicate()]

    return (out, err)
