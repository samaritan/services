import csv
import logging
import os
import re
import tempfile

from .. import parsers
from ..commands import COMMANDS
from ..models import Change, Changes, Commit, Developer, File, Message,       \
                     Module, Move, Moves, Patch

_CHANGE_RE = re.compile(
    r'^(?P<insertions>(?:\d+|\-))\s+(?P<deletions>(?:\d+|\-))\s+(?P<path>.+)'
)
_MOVESPECIFICATION_RE = re.compile(r'^ rename (?P<specification>.*) \(\d+%\)$')

logger = logging.getLogger(__name__)


def _get_changes(lines, commit):
    changes = list()
    for line in lines:
        match = _CHANGE_RE.match(line.strip('\n'))
        insertions, deletions, path = match.groups()
        insertions = None if insertions == '-' else insertions
        deletions = None if deletions == '-' else deletions
        change = Change(path=path, insertions=insertions, deletions=deletions)
        changes.append(change)
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


def _handle_exit(thread):
    if thread:
        thread.join()


class Repository:
    def __init__(self, path, project, runner):
        self._path = path
        self._project = project
        self._runner = runner

    def get_changes(self):
        commits = {c.sha: c for c in self.get_commits()}

        key, command = self._get_key('changes'), COMMANDS['changes']
        ostream, ethread = self._runner.run(command, key=key)

        for sha, lines in parsers.GitLogParser.parse(ostream):
            yield _get_changes(lines, commits[sha])
        _handle_exit(ethread)

    def get_commits(self):
        key, command = self._get_key('commits'), COMMANDS['commits']
        ostream, ethread = self._runner.run(command, key=key)
        for row in csv.reader(ostream):
            yield Commit(*row[:2], Developer(*row[2:4]))
        _handle_exit(ethread)

    def get_content(self, oid):
        command = COMMANDS['content'].format(oid=oid)
        ostream, ethread = self._runner.run(command)
        content = ostream.read()
        _handle_exit(ethread)
        return content

    def get_developers(self):
        key, command = self._get_key('developers'), COMMANDS['developers']
        ostream, ethread = self._runner.run(command, key=key)
        # TODO: See https://github.com/samaritan/services/issues/3 for context
        #       on the use of temporary set to deduplicate developers.
        developers = set()
        # TODO: See https://github.com/samaritan/services/issues/1 for context
        #       on the hardcoded number of fields below.
        for row in csv.reader(ostream):
            developer = Developer(*row[:2])
            if developer not in developers:
                developers.add(developer)
                yield developer
        _handle_exit(ethread)

    def get_files(self):
        active_files = self._get_active_files()

        key, command = self._get_key('files_all'), COMMANDS['files']['all']
        ostream, ethread = self._runner.run(command, key=key)
        for path in ostream:
            path = path.strip('\n')
            mpath = os.path.dirname(path)                        \
                    if os.path.dirname(path) != '' else '(root)'
            yield File(path, path in active_files, Module(mpath))
        _handle_exit(ethread)

    def get_messages(self, commits):
        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = COMMANDS['messages'].format(filename=tfile.name)
            ostream, ethread = self._runner.run(command)
            commits = {c.sha: c for c in commits}
            for sha, lines in parsers.GitLogParser.parse(ostream):
                yield Message(commit=commits[sha], message='\n'.join(lines))
            _handle_exit(ethread)
        finally:
            if tfile is not None and os.path.exists(tfile.name):
                os.remove(tfile.name)

    def get_modules(self):
        modules = set()
        for file_ in self.get_files():
            if file_.module not in modules:
                yield file_.module
                modules.add(file_.module)

    def get_moves(self):
        commits = {c.sha: c for c in self.get_commits()}

        key, command = self._get_key('moves'), COMMANDS['moves']
        ostream, ethread = self._runner.run(command, key=key)

        for sha, lines in parsers.GitLogParser.parse(ostream):
            yield _get_moves(lines, commits[sha])

        _handle_exit(ethread)

    def get_patches(self, commits):
        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = COMMANDS['patches'].format(filename=tfile.name)
            ostream, ethread = self._runner.run(command)
            commits = {c.sha: c for c in commits}
            for sha, lines in parsers.GitLogParser.parse(ostream):
                yield Patch(commit=commits[sha], patch='\n'.join(lines))
            _handle_exit(ethread)
        finally:
            if tfile is not None and os.path.exists(tfile.name):
                os.remove(tfile.name)

    def get_path(self):
        return self._path

    def get_version(self):
        version = None

        command = COMMANDS['version']
        ostream, ethread = self._runner.run(command)
        version = [line.strip('\n') for line in ostream][0]
        _handle_exit(ethread)

        return version

    def _get_active_files(self):
        files = None

        key = self._get_key('files_active')
        command = COMMANDS['files']['active']
        ostream, ethread = self._runner.run(command, key=key)
        files = {path.strip('\n') for path in ostream}
        _handle_exit(ethread)

        return files

    def _get_key(self, item):
        return f'{self._project.name}_{self.get_version()}_{item}'
