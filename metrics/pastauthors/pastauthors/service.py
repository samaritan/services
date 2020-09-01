import logging

from eventlet import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastAuthors
from .schemas import ChangesSchema, CommitSchema, PastAuthorsSchema

logger = logging.getLogger(__name__)


def _get_changes(project, commit, repository_rpc):
    changes = repository_rpc.get_changes(project, commit.sha)
    return ChangesSchema(many=True).load(changes)


def _get_pastauthors(changes):
    pastauthors = list()

    changes = sorted(changes, key=lambda i: i.commit.timestamp)

    paths = dict()
    for change in changes:
        commit = change.commit
        for path in change.changes:
            pauthors = paths.get(path, set()) - {commit.author}
            paths[path] = pauthors | {commit.author}
            pastauthors.append(PastAuthors(
                commit=commit, path=path, pastauthors=len(pauthors)
            ))

    return pastauthors


class PastAuthorsService:
    name = 'pastauthors'

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
        pastauthors = _get_pastauthors(changes)
        if sha is not None:
            pastauthors = [i for i in pastauthors if i.commit.sha == sha]

        return PastAuthorsSchema(many=True).dump(pastauthors)
