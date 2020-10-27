import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        patch = self.repository_rpc.get_patch(project, sha, path)
        if patch:
            vectorizer = CountVectorizer(binary=True)
            vectorizer.fit([patch])
            return vectorizer.get_feature_names()
        return None if patch is None else list()
