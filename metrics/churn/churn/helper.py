import logging

import eventlet

from .models import Churn, FunctionChurn, LineChurn
from .models.enumerations import ChangeType, LineType
from .schemas import CommitSchema, FunctionSchema, LineChangesSchema

logger = logging.getLogger(__name__)


def _get_functionchurn(before, after, lines):
    bnames = {f.name for f in before}
    anames = {f.name for f in after}

    insertions = len(anames - bnames)
    deletions = len(bnames - anames)

    modifications = 0
    for function in (f for f in after if f.name in bnames & anames):
        begin, end = function.lines
        for line in lines:
            if begin <= line <= end:
                modifications += 1
                break

    return FunctionChurn(insertions, deletions, modifications)


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


class Helper:
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
        function = self._get_functionchurn(commit, path, **data)
        return Churn(commit, path, line=line, function=function)

    def _get_linechurn(self, change=None, delta=None):
        insertions, deletions = delta.insertions, delta.deletions
        return LineChurn(insertions, deletions)

    def _get_functions(self, path, oid):
        functions = None
        if self._parser.is_parsable(path):
            contents = self._repository.get_content(self._project, oid)
            functions = self._parser.get_functions(path, contents)
            if functions is not None:
                functions = FunctionSchema(many=True).load(functions)
        return functions

    def _get_functionchurn(self, commit, path, change=None, delta=None):
        function = None

        if change is not None:
            before = self._get_functions(path, change.oids.before)
            after = self._get_functions(path, change.oids.after)
            lines = None
            if change.type == ChangeType.MODIFIED:
                lines = self._get_lineschanged(commit, path)

            # `before` and `after` are None iff `path` is not parsed (either
            #   because there is no parser to parse language that `path` is
            #   written in or because there was an error when parsing `path`.
            if before is not None and after is not None:
                function = _get_functionchurn(before, after, lines)

        return function

    def _get_lineschanged(self, commit, path):
        commit = CommitSchema().dump(commit)
        linechanges = self._repository.get_linechanges(self._project, commit)
        linechanges = LineChangesSchema().load(linechanges)

        inserted = linechanges.linechanges[path][LineType.INSERTED.value]
        deleted = linechanges.linechanges[path][LineType.DELETED.value]

        return sorted(inserted + deleted)
