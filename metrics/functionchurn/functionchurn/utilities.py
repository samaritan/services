import hashlib
import logging

logger = logging.getLogger(__name__)


def hashit(data):
    return hashlib.sha1(data.encode()).hexdigest()
