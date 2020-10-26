import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy
from sklearn.feature_extraction.text import CountVectorizer

from .schemas import PatchSchema

logger = logging.getLogger(__name__)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        patch = self.repository_rpc.get_patch(project, sha)
        patch = PatchSchema().load(patch)

        if patch.patch:
            vectorizer = CountVectorizer(binary=True)
            vectorizer.fit([patch.patch])
            return vectorizer.get_feature_names()
        return None if patch.patch is None else list()
