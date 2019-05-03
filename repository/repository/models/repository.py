import csv
import logging
import os
import re
import tempfile
import threading

import eventlet

from zope.interface.declarations import implementer

from . import irepository
from .. import parsers, utilities
from ..models import Change, Changes, Commit, Developer, File, Module, Patch

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


def _log_error(stream):
    error = stream.read()
    if error != '':
        logger.error(error)


@implementer(irepository.IRepository)
class Repository:
    def __init__(self, path, processes):
        self._path = path
        self._processes = processes

    def get_changes(self):
        changeslist = list()

        commits = {c.sha: c for c in self.get_commits()}

        command = 'git log --no-merges --no-renames --numstat --pretty=%H'
        ostream, ethread = self._run(command)

        lines, indices, shas = parsers.GitLogParser.parse(ostream)

        indices.append(len(lines))
        arguments = [
            (lines[b + 2:e], commits[sha])
            for b, e, sha in zip(indices[:-1], indices[1:], shas)
        ]

        pool = eventlet.GreenPool()
        for changes in pool.starmap(_get_changes, arguments):
            changeslist.append(changes)
        ethread.join()

        return changeslist

    def get_commits(self):
        commits = None

        command = 'git log --no-merges --pretty=\'"%H","%ct","%aN","%aE"\''
        ostream, ethread = self._run(command)
        commits = [
            Commit(*row[:2], Developer(*row[2:4]))
            for row in csv.reader(ostream)
        ]
        ethread.join()

        return commits

    def get_developers(self):
        developers = None

        command = 'git log --no-merges --pretty=\'"%aN","%aE"\'| sort -u'

        ostream, ethread = self._run(command)
        # TODO: See https://github.com/samaritan/services/issues/1 for context
        #       on the hardcoded number of fields below.
        developers = [Developer(*row[:2]) for row in csv.reader(ostream)]
        ethread.join()

        return developers

    def get_files(self):
        files = None

        active_files = self._get_active_files()

        command = 'git log --no-merges --pretty= --name-only | sort -u'
        ostream, ethread = self._run(command)
        files = list()
        for path in ostream:
            path = path.strip('\n')
            mpath = os.path.dirname(path)                        \
                    if os.path.dirname(path) != '' else '(root)'
            files.append(File(path, path in active_files, Module(mpath)))
        ethread.join()

        return files

    def get_modules(self):
        return list({f.module for f in self.get_files()})

    def get_patches(self, commits):
        patches = None

        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = f'cat {tfile.name} | '                            \
                       'xargs git show --no-merges --patch --pretty=%H'
            ostream, ethread = self._run(command)
            lines, indices, shas = parsers.GitLogParser.parse(ostream)

            indices.append(len(lines))
            commits = {c.sha: c for c in commits}
            patches = [
                Patch(commit=commits[sha], patch=''.join(lines[b + 2:e]))
                for b, e, sha in zip(indices[:-1], indices[1:], shas)
            ]
            ethread.join()
        finally:
            if tfile is not None and os.path.exists(tfile.name):
                os.remove(tfile.name)

        return patches

    def get_path(self):
        return self._path

    def get_version(self):
        version = None

        command = 'git log --no-merges -1 --pretty=%h'
        ostream, ethread = self._run(command)
        version = [line.strip('\n') for line in ostream][0]
        ethread.join()

        return version

    def _get_active_files(self):
        files = None

        command = 'git ls-files'
        ostream, ethread = self._run(command)
        files = {path.strip('\n') for path in ostream}
        ethread.join()

        return files

    def _run(self, command):
        ostream, estream = utilities.run(command, work_dir=self._path)

        thread = threading.Thread(target=_log_error, args=(estream,))
        thread.start()

        return ostream, thread
