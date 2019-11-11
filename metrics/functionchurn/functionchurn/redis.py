import redis

from nameko.extensions import DependencyProvider

REDIS_URL_KEY = 'REDIS_URL'


class Redis(DependencyProvider):
    def get_dependency(self, worker_ctx):
        url = self.container.config[REDIS_URL_KEY]
        return redis.Redis.from_url(url)
