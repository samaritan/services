import io
import json
import logging

from . import utilities
from .models import Loc

logger = logging.getLogger(__name__)


class SourceCode:
    def __init__(self, path, processes):
        self.path = path
        self.processes = processes

    def get_loc(self):
        locs = None

        command = f'cloc --processes={self.processes} --quiet --by-file ' \
                   '--json .'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            locs = list()
            for (path, data) in json.load(stream).items():
                if path in {'header', 'SUM'}:
                    continue
                path = path.lstrip('./')
                bloc, cloc, sloc = data['blank'], data['comment'], data['code']
                locs.append(Loc(path=path, bloc=bloc, cloc=cloc, sloc=sloc))
        return locs

    def _get_output(self, commands):
        (out, err) = utilities.run(commands, work_dir=self.path)
        if err != '':
            logger.error(err)
        return out
