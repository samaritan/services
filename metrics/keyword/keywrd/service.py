import logging
import os

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .exceptions import LanguageNotSupported
from .keywrd import Keywrd
from .schemas import CommitSchema, KeywordSchema, PatchSchema, ProjectSchema

logger = logging.getLogger(__name__)


def _get_keyword(project, commit, keyword, repository_rpc):
    patch = repository_rpc.get_patch(project.name, commit.sha)
    patch = PatchSchema().load(patch)
    return keyword.get(patch)


class KeywordService:
    name = 'keyword'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        if project.language.lower() not in self.config['KEYWORDS']:
            raise LanguageNotSupported(f'{project.language} not supported')
        keywords = self.config['KEYWORDS'].get(project.language.lower())

        keywrd = Keywrd(keywords=keywords)
        commits = None
        if sha is None:
            commits = self.repository_rpc.get_commits(project.name)
        else:
            commits = [self.repository_rpc.get_commit(project.name, sha)]
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool(os.cpu_count())
        arguments = (
            (project, c, keywrd, self.repository_rpc) for c in commits
        )
        keyword = list()
        for item in pool.starmap(_get_keyword, arguments):
            keyword.append(item)

        return KeywordSchema(many=True).dump(keyword)
