import logging

from eventlet import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastChanges
from .schemas import ChangesSchema, CommitSchema, PastChangesSchema

logger = logging.getLogger(__name__)


def _get_changes(project, commit, repository_rpc):
    changes = repository_rpc.get_changes(project, commit.sha)
    return ChangesSchema(many=True).load(changes)


def _get_pastchanges(changes):
    pastchanges = list()

    changes = sorted(changes, key=lambda i: i.commit.timestamp)

    paths = dict()
    for change in changes:
        commit = change.commit
        for path in change.changes:
            pchanges = paths.get(path, 0)
            paths[path] = pchanges + 1
            pastchanges.append(PastChanges(
                commit=commit, path=path, pastchanges=pchanges
            ))

    return pastchanges


class PastChangesService:
    name = 'pastchanges'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha)
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool()
        arguments = [(project, c, self.repository_rpc) for c in commits]
        changes = list()
        for item in pool.starmap(_get_changes, arguments):
            changes.extend(item)
        pastchanges = _get_pastchanges(changes)
        if sha is not None:
            pastchanges = [i for i in pastchanges if i.commit.sha == sha]

        return PastChangesSchema(many=True).dump(pastchanges)
