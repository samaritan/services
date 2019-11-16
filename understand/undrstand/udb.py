import contextlib
import logging
import os
import shutil

import understand

from . import utilities

_RELATIVE_PREFIX = 'RELATIVE:/'
logger = logging.getLogger(__name__)


def _get_name(entity, type_):
    if type_ == 'function':
        return f'{entity.simplename()}({entity.parameters()})'
    return entity.relname().replace(_RELATIVE_PREFIX, '')


def _get_file(entity):
    while entity is not None:
        if entity.parent() is not None:
            type_ = _get_type(entity.parent())
            if type_ == 'file':
                return _get_name(entity.parent(), type_)
        entity = entity.parent()


def _get_type(entity):
    if entity.kind().check('function,procedure,method'):
        return 'function'
    if entity.kind().check('file'):
        return 'file'
    return None


@contextlib.contextmanager
def _open_udb(path):
    udb = None
    try:
        udb = understand.open(path)
        yield udb
    finally:
        if udb is not None:
            udb.close()


class UDB:
    def __init__(self, root, name, source_language, source_path):
        self._root = root
        self._name = name
        self._source_language = 'c++' if source_language == 'c' \
                                 else source_language
        self._source_path = source_path

    def analyze(self):
        if not self.exists:
            self.create()

        command = f'und -quiet analyze {self._name}'
        _ = self._get_output(command)
        self._move()

    def create(self):
        if self.exists:
            return

        command = f'und -quiet create -languages {self._source_language} ' \
                  f'{self._name}'
        _ = self._get_output(command)
        logger.debug('%s created', self._name)

        command = f'und -quiet settings -AddMode Relative {self._name}'
        _ = self._get_output(command)
        command = f'und -quiet add . {self._name}'
        _ = self._get_output(command)
        logger.debug('%s added to %s', self._source_path, self._name)

    def get_metrics(self, metrics):
        if not self.exists:
            self.analyze()

        values = list()
        with _open_udb(self._udb_path) as udb:
            for entity in udb.ents('file,function,procedure,method'):
                type_ = _get_type(entity)
                uid = entity.id()
                name = _get_name(entity, type_)
                path = name if type_ == 'file' else _get_file(entity)
                _entity = (uid, name, type_, path)
                values.append((_entity, entity.metric(metrics)))
        return values

    @property
    def exists(self):
        return os.path.exists(self._udb_path)

    @property
    def _udb_path(self):
        return os.path.join(self._root, self._name)

    def _get_output(self, command):
        (out, err) = utilities.run(command, work_dir=self._source_path)
        if err != '':
            logger.error(err)
        return out

    def _move(self):
        source = os.path.join(self._source_path, self._name)
        destination = self._udb_path
        shutil.move(source, destination)
        logger.debug('Moved %s to %s', source, destination)
