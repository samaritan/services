import logging

import eventlet

from .models import Churn, LineChurn

logger = logging.getLogger(__name__)


class ChurnHelper:
    def __init__(self, project, repository):
        self._project = project.name
        self._repository = repository

    def collect(self, deltas):
        arguments = (
            (d.commit, p, dd)
            for d in deltas for (p, dd) in d.deltas.items()
        )
        pool = eventlet.GreenPool(100)
        for churn in pool.starmap(self._get_churn, arguments):
            yield churn

    def _get_churn(self, commit, path, delta):
        line = self._get_linechurn(delta)
        function = None
        return Churn(commit, path, line=line, function=function)

    def _get_linechurn(self, delta):
        insertions, deletions = delta.insertions, delta.deletions
        return LineChurn(insertions, deletions)
