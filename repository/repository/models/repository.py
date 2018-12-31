import csv
import io
import logging
import os
import re

from zope.interface.declarations import implementer

from . import irepository
from .. import utilities
from ..models import Change, Changes, Commit, Developer, File, Module

_CHANGE_RE = re.compile(
    r'^(?P<insertions>(?:\d+|\-))\s+(?P<deletions>(?:\d+|\-))\s+(?P<path>.+)'
)
_SHA_RE = re.compile(r'^(?P<sha>.{40})$')

logger = logging.getLogger(__name__)


@implementer(irepository.IRepository)
class Repository:
    def __init__(self, path, processes):
        self._path = path
        self._processes = processes

    def get_commits(self):
        commits = None

        command = ['git log --no-merges --pretty=\'"%H","%ct","%aN","%aE"\'']
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            commits = [
                Commit(*row[:2], Developer(*row[2:]))
                for row in csv.reader(stream)
            ]

        return commits

    def get_changes(self):
        changeslist = list()

        commits = {c.sha: c for c in self.get_commits()}

        command = 'git log --no-merges --no-renames --numstat --pretty=%H'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            lines = stream.readlines()

            index = 0
            while (index + 1) < len(lines):
                sha = _SHA_RE.match(lines[index]).groupdict().get('sha')
                index += 1
                if lines[index].strip('\n') == '':
                    changes = list()
                    index += 1  # Ignore the empty line after SHA
                    # Process the list of changes associated with the SHA
                    while (index < len(lines) and
                           _CHANGE_RE.match(lines[index].strip('\n'))):
                        match = _CHANGE_RE.match(lines[index].strip('\n'))
                        changes.append(Change(**match.groupdict()))
                        index += 1
                changeslist.append(Changes(
                    commit=commits[sha], changes=changes
                ))

        return changeslist

    def get_developers(self):
        developers = None

        command = 'git log --no-merges --pretty=\'"%aN","%aE"\'| sort -u'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            developers = [Developer(*row) for row in csv.reader(stream)]

        return developers

    def get_files(self):
        files = None

        active_files = self._get_active_files()

        command = 'git log --no-merges --pretty= --name-only | sort -u'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            files = list()
            for path in stream:
                path = path.strip('\n')
                mpath = os.path.dirname(path)                        \
                        if os.path.dirname(path) != '' else '(root)'
                files.append(File(path, path in active_files, Module(mpath)))

        return files

    def get_modules(self):
        return list({f.module for f in self.get_files()})

    def get_path(self):
        return self._path

    def _get_active_files(self):
        files = None

        command = 'git ls-files'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            files = {path.strip('\n') for path in stream}

        return files

    def _get_output(self, command):
        (out, err) = utilities.run(command, work_dir=self._path)
        if err != '':
            logger.error(err)
        return out
