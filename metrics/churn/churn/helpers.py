import logging

import eventlet

from .models import Churn, FunctionChurn, LineChurn
from .models.enumerations import ChangeType
from .schemas import FunctionSchema

logger = logging.getLogger(__name__)


def _unpack_deltas(deltas):
    items = ((d.commit, p, dd) for d in deltas for p, dd in d.deltas.items())
    for (commit, path, delta) in items:
        yield (commit, path, 'delta', delta)


def _unpack_changes(changes):
    items = ((c.commit, p, cc) for c in changes for p, cc in c.changes.items())
    for (commit, path, change) in items:
        yield (commit, path, 'change', change)


def _update(data, part):
    for (commit, path, key, value) in part:
        if (commit, path) not in data:
            data[(commit, path)] = dict()
        data[(commit, path)].update({key: value})


def _pack(changes, deltas):
    data = dict()
    _update(data, _unpack_deltas(deltas))
    _update(data, _unpack_changes(changes))
    return data


class ChurnHelper:
    def __init__(self, project, repository, parser):
        self._project = project.name
        self._repository = repository
        self._parser = parser

    def collect(self, changes, deltas):
        data = _pack(changes, deltas)
        arguments = ((c, p, d) for ((c, p), d) in data.items())
        pool = eventlet.GreenPool()
        for churn in pool.starmap(self._get_churn, arguments):
            yield churn

    def _get_churn(self, commit, path, data):
        line = self._get_linechurn(**data)
        function = self._get_functionchurn(path, **data)
        return Churn(commit, path, line=line, function=function)

    def _get_linechurn(self, change=None, delta=None):
        insertions, deletions = delta.insertions, delta.deletions
        return LineChurn(insertions, deletions)

    def _get_functions(self, path, oid):
        contents = self._repository.get_content(self._project, oid)
        functions = self._parser.get_functions(path, contents)
        if functions is not None:
            functions = FunctionSchema(many=True).load(functions)
        return functions

    def _get_functionnames(self, path, oid):
        functions = self._get_functions(path, oid)
        if functions is not None:
            functions = {i.name for i in functions} if functions else set()
        return functions

    def _get_functionchurn(self, path, change=None, delta=None):
        function = None

        if change is not None:
            functions = None

            if change.type == ChangeType.ADDED:
                functions = self._get_functionnames(path, change.oids.after)
                if functions is not None:
                    functions = [('i', f) for f in functions]
            elif change.type == ChangeType.DELETED:
                functions = self._get_functionnames(path, change.oids.before)
                if functions is not None:
                    functions = [('d', f) for f in functions]

            if functions:
                insertions = len([f for (s, f) in functions if s == 'i'])
                deletions = len([f for (s, f) in functions if s == 'd'])
                function = FunctionChurn(insertions, deletions)
        return function
