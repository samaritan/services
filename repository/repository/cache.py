import diskcache

from nameko.extensions import DependencyProvider

CACHE_ROOT_KEY = 'CACHE_ROOT'


class Cache(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return diskcache.Cache(self.container.config[CACHE_ROOT_KEY])
