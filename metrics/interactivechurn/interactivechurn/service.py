import logging

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import InteractiveChurn
from .schemas import CommitSchema, InteractiveChurnSchema,                    \
                     LastModifierSchema, LineChangesSchema

logger = logging.getLogger(__name__)


def _get_interactivechurn(project, commit, repository_rpc):
    ichurns = list()

    linechanges = _get_linechanges(project, commit, repository_rpc)
    for path in linechanges.linechanges:
        deletions = linechanges.linechanges[path]['-']
        if not deletions:
            ichurns.append(InteractiveChurn(commit, path, 0.0))
            continue

        lastmodifiers = _get_lastmodifiers(
            project, commit, path, deletions, repository_rpc
        )
        authors = (i.commit.author for i in lastmodifiers)
        ichurn = sum(i != commit.author for i in authors) / len(deletions)
        ichurns.append(InteractiveChurn(commit, path, ichurn))

    return ichurns


def _get_lastmodifiers(project, commit, path, lines, repository_rpc):
    commit = CommitSchema().dump(commit)
    lastmodifiers = repository_rpc.get_lastmodifiers(
        project, commit, path, lines
    )
    return LastModifierSchema(many=True).load(lastmodifiers)


def _get_linechanges(project, commit, repository_rpc):
    commit = CommitSchema().dump(commit)
    linechanges = repository_rpc.get_linechanges(project, commit)
    return LineChangesSchema().load(linechanges)


class InteractiveChurnService:
    name = 'interactivechurn'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        commits = self._get_commits(project)

        pool = GreenPool()
        arguments = [(project, c, self.repository_rpc) for c in commits]
        interactivechurn = list()
        for item in pool.starmap(_get_interactivechurn, arguments):
            interactivechurn.extend(item)
        return InteractiveChurnSchema(many=True).dump(interactivechurn)

    def _get_commits(self, project):
        commits = self.repository_rpc.get_commits(project)
        return CommitSchema(many=True).load(commits)
