import redis

from nameko.extensions import DependencyProvider

REDIS_URI_KEY = 'REDIS_URI'


class Redis(DependencyProvider):
    def setup(self):
        self._client = redis.StrictRedis.from_url(
            self.container.config.get(REDIS_URI_KEY)
        )

    def get_dependency(self, worker_ctx):
        return self._client
