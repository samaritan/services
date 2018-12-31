import csv
import logging
import os

logger = logging.getLogger(__name__)


class CSV:
    @staticmethod
    def read(path):
        data = list()

        if os.path.exists(path):
            with open(path) as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
            logger.debug('Read %d rows from %s', len(data), path)

        return data
