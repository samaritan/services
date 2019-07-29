import diskcache

from nameko.extensions import DependencyProvider

CACHE_ROOT_KEY = 'CACHE_ROOT'


class Cache(DependencyProvider):
    def get_dependency(self, worker_ctx):
        directory = self.container.config[CACHE_ROOT_KEY]
        return diskcache.Cache(directory, eviction_policy='none')
