import csv
import io
import logging
import os
import re

import eventlet

from zope.interface.declarations import implementer

from . import irepository
from .. import parsers, utilities
from ..models import Change, Changes, Commit, Developer, File, Module

_CHANGE_RE = re.compile(
    r'^(?P<insertions>(?:\d+|\-))\s+(?P<deletions>(?:\d+|\-))\s+(?P<path>.+)'
)

logger = logging.getLogger(__name__)


def _get_changes(lines, commit):
    changes = list()
    for line in lines:
        match = _CHANGE_RE.match(line.strip('\n'))
        changes.append(Change(**match.groupdict()))
    return Changes(commit=commit, changes=changes)


@implementer(irepository.IRepository)
class Repository:
    def __init__(self, path, processes):
        self._path = path
        self._processes = processes

    def get_commits(self):
        commits = None

        command = 'git log --no-merges --pretty=\'"%H","%ct","%aN","%aE"\''
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            commits = [
                Commit(*row[:2], Developer(*row[2:4]))
                for row in csv.reader(stream)
            ]

        return commits

    def get_changes(self):
        changeslist = list()

        commits = {c.sha: c for c in self.get_commits()}

        command = 'git log --no-merges --no-renames --numstat --pretty=%H'
        output = self._get_output(command)
        with io.StringIO(output) as stream:
            lines, indices, shas = parsers.GitLogParser.parse(stream)

            indices.append(len(lines))
            arguments = [
                (lines[b + 2:e], commits[sha])
                for b, e, sha in zip(indices[:-1], indices[1:], shas)
            ]

            pool = eventlet.GreenPool()
            for changes in pool.starmap(_get_changes, arguments):
                changeslist.append(changes)

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
