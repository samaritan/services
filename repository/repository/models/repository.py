import csv
import logging
import os
import re
import tempfile
import threading

from zope.interface.declarations import implementer

from . import irepository
from .. import parsers, utilities
from ..models import Change, Changes, Commit, Developer, File, Module, Move, \
                     Moves, Patch

_CHANGE_RE = re.compile(
    r'^(?P<insertions>(?:\d+|\-))\s+(?P<deletions>(?:\d+|\-))\s+(?P<path>.+)'
)
_MOVESPECIFICATION_RE = re.compile(r'^ rename (?P<specification>.*) \(\d+%\)$')

logger = logging.getLogger(__name__)


def _handle_exit(process, stream):
    process.wait()
    logger.debug('%s returned %d', process.args, process.returncode)

    error = stream.read()
    if error != '':
        logger.error(error)


def _get_changes(lines, commit):
    changes = list()
    for line in lines:
        match = _CHANGE_RE.match(line.strip('\n'))
        changes.append(Change(**match.groupdict()))
    return Changes(commit=commit, changes=changes)


def _get_indices(specification):
    lbrace, arrow, rbrace = None, None, None
    for (index, character) in enumerate(specification):
        if character == '{':
            lbrace = index
        elif character == '}':
            rbrace = index
            break
        elif character == '|':
            arrow = index
    return lbrace, arrow, rbrace


def _get_components(specification):
    specification = specification.replace(' => ', '|')
    lbrace, arrow, rbrace = _get_indices(specification)

    # Expected format of specification is afixed{avariable => bvariable}bfixed
    afixed, avariable, bvariable, bfixed = [''] * 4
    if lbrace is None and rbrace is None:
        avariable = specification[0:arrow]
        bvariable = specification[arrow + 1: len(specification)]
    else:
        afixed = specification[0:lbrace]
        avariable = specification[lbrace + 1:arrow]
        bvariable = specification[arrow + 1:rbrace]
        bfixed = specification[rbrace + 1:len(specification)]
    return afixed, avariable, bvariable, bfixed


def _get_move(line):
    move = None
    match = _MOVESPECIFICATION_RE.match(line)
    if match:
        specification = match.groupdict().get('specification')
        afixed, avariable, bvariable, bfixed = _get_components(specification)
        source = '{}{}{}'.format(afixed, avariable, bfixed).replace('//', '/')
        destination = '{}{}{}'.format(afixed, bvariable, bfixed) \
                              .replace('//', '/')
        move = Move(source=source, destination=destination)
    return move


def _get_moves(lines, commit):
    moves = list()
    for line in lines:
        move = _get_move(line)
        if move is not None:
            moves.append(move)
    return Moves(commit=commit, moves=moves)


@implementer(irepository.IRepository)
class Repository:
    def __init__(self, path, processes):
        self._path = path
        self._processes = processes

    def get_changes(self):
        commits = {c.sha: c for c in self.get_commits()}

        command = 'git log --no-merges --no-renames --numstat --pretty=*%n%H'
        ostream, ethread = self._run(command)

        for sha, lines in parsers.GitLogParser.parse(ostream):
            yield _get_changes(lines, commits[sha])

        ethread.join()

    def get_commits(self):
        command = 'git log --no-merges --pretty=\'"%H","%ct","%aN","%aE"\''
        ostream, ethread = self._run(command)
        for row in csv.reader(ostream):
            yield Commit(*row[:2], Developer(*row[2:4]))
        ethread.join()

    def get_developers(self):
        command = 'git log --no-merges --pretty=\'"%aN","%aE"\'| sort -u'

        ostream, ethread = self._run(command)
        # TODO: See https://github.com/samaritan/services/issues/1 for context
        #       on the hardcoded number of fields below.
        for row in csv.reader(ostream):
            yield Developer(*row[:2])
        ethread.join()

    def get_files(self):
        active_files = self._get_active_files()

        command = 'git log --no-merges --pretty= --name-only | sort -u'
        ostream, ethread = self._run(command)
        for path in ostream:
            path = path.strip('\n')
            mpath = os.path.dirname(path)                        \
                    if os.path.dirname(path) != '' else '(root)'
            yield File(path, path in active_files, Module(mpath))
        ethread.join()

    def get_modules(self):
        modules = set()
        for file_ in self.get_files():
            if file_.module not in modules:
                yield file_.module
                modules.add(file_.module)

    def get_moves(self):
        commits = {c.sha: c for c in self.get_commits()}

        command = 'git log -M100% --diff-filter=R --summary --pretty=*%n%H'
        ostream, ethread = self._run(command)

        for sha, lines in parsers.GitLogParser.parse(ostream):
            yield _get_moves(lines, commits[sha])

        ethread.join()

    def get_patches(self, commits):
        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = f'cat {tfile.name} | '                            \
                       'xargs git show --no-merges --patch --pretty=*%n%H'
            ostream, ethread = self._run(command)
            commits = {c.sha: c for c in commits}
            for sha, lines in parsers.GitLogParser.parse(ostream):
                yield Patch(commit=commits[sha], patch='\n'.join(lines))
            ethread.join()
        finally:
            if tfile is not None and os.path.exists(tfile.name):
                os.remove(tfile.name)

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
        process, ostream, estream = utilities.run(command, work_dir=self._path)

        thread = threading.Thread(
            target=_handle_exit, args=(process, estream,)
        )
        thread.start()

        return ostream, thread
