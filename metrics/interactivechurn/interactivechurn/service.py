import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import InteractiveChurn
from .schemas import CommitSchema, InteractiveChurnSchema,                    \
                     LastModifierSchema, LineChangesSchema

logger = logging.getLogger(__name__)


def _get_interactivechurn(project, commit, path, repository_rpc):
    linechanges = _get_linechanges(project, commit, path, repository_rpc)

    deletions = linechanges.linechanges[path]['-']
    if not deletions:
        return InteractiveChurn(commit, path, 0.0)

    lastmodifiers = _get_lastmodifiers(
        project, commit, path, deletions, repository_rpc
    )
    authors = (i.commit.author for i in lastmodifiers)
    ichurn = sum(i != commit.author for i in authors) / len(deletions)
    return InteractiveChurn(commit, path, ichurn)


def _get_lastmodifiers(project, commit, path, lines, repository_rpc):
    commit = CommitSchema().dump(commit)
    lastmodifiers = repository_rpc.get_lastmodifiers(
        project, commit, path, lines
    )
    return LastModifierSchema(many=True).load(lastmodifiers)


def _get_linechanges(project, commit, path, repository_rpc):
    commit = CommitSchema().dump(commit)
    linechanges = repository_rpc.get_linechanges(project, commit, path)
    return LineChangesSchema().load(linechanges)


class InteractiveChurnService:
    name = 'interactivechurn'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commit = self._get_commit(project, sha)

        interactivechurn = _get_interactivechurn(
            project, commit, path, self.repository_rpc
        )
        return InteractiveChurnSchema().dump(interactivechurn)

    def _get_commit(self, project, sha):
        commit = self.repository_rpc.get_commit(project, sha)
        return CommitSchema().load(commit)
