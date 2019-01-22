import contextlib
import logging
import os

import understand

from . import utilities

logger = logging.getLogger(__name__)


def _get_name(entity):
    name = None

    type_ = _get_type(entity)
    if type_ == 'function':
        name = f'{entity.simplename()}({entity.parameters()})'
    elif type_ == 'file':
        name = entity.relname()

    return name


def _get_file(entity):
    file_ = None

    while entity is not None:
        if entity.parent() is not None and \
           _get_type(entity.parent()) == 'file':
            file_ = entity.parent().relname()
            break
        entity = entity.parent()

    return file_


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
    def __init__(self, path, source_language, source_path):
        self._path = path
        self._source_language = 'c++' if source_language == 'c' \
                                 else source_language
        self._source_path = source_path

        self._metrics = None  # Cache for list of available metrics

    def analyze(self):
        if not self.exists:
            self.create()

        command = f'und -quiet analyze {self._path}'
        _ = self._get_output(command)

    def create(self):
        if self.exists:
            return

        command = f'und -quiet create -languages {self._source_language} ' \
                  f'{self._path}'
        _ = self._get_output(command)
        logger.debug('%s created', self._path)

        command = f'und -quiet add {self._source_path} {self._path}'
        _ = self._get_output(command)
        logger.debug('%s added to %s', self._source_path, self._path)

    def get_metrics(self, metrics):
        if not self.exists:
            self.analyze()

        metrics = self._filter_metrics(metrics)
        if not metrics:
            return None

        values = list()
        with _open_udb(self._path) as udb:
            for entity in udb.ents('file,function,procedure,method'):
                uid = entity.id()
                name = _get_name(entity)
                type_ = _get_type(entity)
                path = name if type_ == 'file' else _get_file(entity)
                _entity = (uid, name, type_, path)

                values.append((_entity, entity.metric(metrics)))
        return values

    @property
    def exists(self):
        return os.path.exists(self._path)

    @property
    def metrics(self):
        if self._metrics is None:
            with _open_udb(self._path) as udb:
                self._metrics = set(udb.metrics())
        return self._metrics

    def _get_output(self, command):
        (out, err) = utilities.run(command)
        if err != '':
            logger.error(err)
        return out

    def _filter_metrics(self, metrics):
        _metrics = list(filter(lambda m: m in self.metrics, metrics))
        if _metrics:
            if len(_metrics) != len(metrics):
                invalid = ','.join(set(metrics) - set(_metrics))
                logger.warning('%s unavailable for %s', invalid, self._path)
            return _metrics

        logger.error('%s unavailable for %s', ','.join(metrics), self._path)
        return None
