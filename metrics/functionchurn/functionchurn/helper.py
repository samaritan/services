import logging

import eventlet

from .models import FunctionChurn
from .models.enumerations import ChangeType, LineType
from .schemas import FunctionSchema, LineChangesSchema

logger = logging.getLogger(__name__)


def _get_functionchurn(before, after, lines):
    before = list() if before is None else before  # File could have been added
    after = list() if after is None else after  # File could have been deleted

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

    return (insertions, deletions, modifications)


def _translate(components):
    return (None if c == -1 else c for c in components)


class Helper:
    def __init__(self, project, repository, parser):
        self._project = project.name
        self._repository = repository
        self._parser = parser

    def collect(self, changes):
        changes = (
            (c.commit, p, cc) for c in changes for p, cc in c.changes.items()
        )
        pool = eventlet.GreenPool()
        for item in pool.starmap(self._get_functionchurn, changes):
            yield item

    def _get_functionchurn(self, commit, path, change):
        before = self._get_functions(path, change.oids.before)
        after = self._get_functions(path, change.oids.after)
        lines = None
        if change.type == ChangeType.MODIFIED:
            lines = self._get_lineschanged(commit, path)

        # `before` and `after` are None iff `path` is not parsed (either
        #   because there is no parser to parse language that `path` is
        #   written in (or) there was an error when parsing `path`.
        components = (-1, -1, -1)
        if before is not None or after is not None:
            components = _get_functionchurn(before, after, lines)
        return FunctionChurn(*_translate(components))

    def _get_functions(self, path, oid):
        functions = None
        if self._parser.is_parsable(path):
            contents = self._repository.get_content(self._project, oid)
            if contents:
                functions = self._parser.get_functions(path, contents)
        return FunctionSchema(many=True).load(functions) if functions else None

    def _get_lineschanged(self, commit, path):
        linechanges = self._repository.get_linechanges(
            self._project, commit.sha
        )
        linechanges = LineChangesSchema().load(linechanges)

        inserted = linechanges.linechanges[path][LineType.INSERTED.value]
        deleted = linechanges.linechanges[path][LineType.DELETED.value]

        return sorted(inserted + deleted)
