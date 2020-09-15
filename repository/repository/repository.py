import csv
import logging
import os
import re
import tempfile

import pygit2

from . import parsers
from .exceptions import CommitNotFound
from .commands import COMMANDS
from .models import Change, Changes, Commit, Delta, Deltas, Developer, File, \
                    LastModifier, LineChanges, Message, Module, Move, Moves, \
                    Oids, Patch
from .models.enumerations import ChangeType, LineType

_CHANGETYPE_MAP = {
    'A': ChangeType.ADDED, 'C': ChangeType.COPIED, 'D': ChangeType.DELETED,
    'M': ChangeType.MODIFIED, 'R': ChangeType.RENAMED,
    'T': ChangeType.TYPECHANGE
}
_DELTA_RE = re.compile(
    r'^(?P<insertions>(?:\d+|\-))\s+(?P<deletions>(?:\d+|\-))\s+(?P<path>.+)'
)
_MOVESPECIFICATION_RE = re.compile(r'^ rename (?P<specification>.*) \(\d+%\)$')
_SPACE_RE = re.compile(r'\s+')

logger = logging.getLogger(__name__)


def _collapse(data):
    i = 0
    while i < len(data):
        j = i + 1
        while j < len(data) and data[j] - data[j - 1] == 1:
            j += 1
        yield (data[i], data[j - 1])
        i = j


def _get_changes(lines, commit):
    changes = dict()
    for line in lines:
        components = _SPACE_RE.split(line)
        path, type_ = components[-1], _CHANGETYPE_MAP[components[4]].value
        oids = Oids(before=components[2], after=components[3])
        changes[path] = Change(type=type_, oids=oids)
    return Changes(commit=commit, changes=changes)


def _get_deltas(lines, commit):
    deltas = dict()
    for line in lines:
        match = _DELTA_RE.match(line.strip('\n'))
        insertions, deletions, path = match.groups()
        insertions = None if insertions == '-' else insertions
        deletions = None if deletions == '-' else deletions
        deltas[path] = Delta(insertions=insertions, deletions=deletions)
    return Deltas(commit=commit, deltas=deltas)


def _get_diff(commit):
    ctree = commit.tree
    if commit.parents:
        parent = commit.parents[0]
        return ctree.diff_to_tree(parent.tree, context_lines=0, swap=True)
    return ctree.diff_to_tree(context_lines=0, swap=True)


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


def _get_linechanges(patch):
    linechanges = {'+': list(), '-': list()}
    for line in (l for h in patch.hunks for l in h.lines):
        if line.origin == LineType.INSERTED.value:
            linechanges[line.origin].append(line.new_lineno)
        if line.origin == LineType.DELETED.value:
            linechanges[line.origin].append(line.old_lineno)
    return linechanges


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
        self._pygit_repository = pygit2.Repository(path)

    def get_changes(self, sha):
        yield from self._get_changes_for_sha(sha)

    def get_commit(self, sha):
        if sha not in self._pygit_repository:
            msg = f'No commit identified by `{sha}` in `{self._project.name}`'
            raise CommitNotFound(msg)

        commit = None

        command = COMMANDS['commits']['commit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)
        for row in csv.reader(ostream):
            commit = Commit(*row[:2], Developer(*row[2:4]))
        _handle_exit(ethread)

        return commit

    def get_commits(self, sha=None):
        if sha is None:
            yield from self._get_commits()
        else:
            yield from self._get_commits_till_sha(sha)

    def get_content(self, oid):
        if oid in self._pygit_repository:
            blob = self._pygit_repository[oid]
            if not blob.is_binary:
                return blob.data.decode(errors='replace')
        return None

    def get_deltas(self, sha):
        yield from self._get_deltas_for_sha(sha)

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
        paths = set()
        for _, lines in parsers.GitLogParser.parse(ostream):
            paths |= set(lines)
        for path in paths:
            path = path.strip('\n')
            mpath = os.path.dirname(path)                        \
                    if os.path.dirname(path) != '' else '(root)'
            yield File(path, path in active_files, Module(mpath))
        _handle_exit(ethread)

    # TODO: Fix the off-by-one bug in the line number. See
    #       https://github.com/samaritan/services/issues/10 for more
    #       information.
    def get_lastmodifiers(self, commit, path, lines):
        _lines = set(lines)
        command = COMMANDS['lastmodifiers']
        lines = ' '.join(f'-L {a},{b}' for a, b in _collapse(lines))
        command = command.format(sha=commit.sha, lines=lines, path=path)
        ostream, ethread = self._runner.run(command)
        for line in ostream:
            components = line.split()
            line = line[line[:line.find(')')].rfind(' ') + 1:line.find(')')]
            line = int(line)
            commit = self.get_commit(components[0])
            if line in _lines:
                yield LastModifier(line=int(line), commit=commit)
            else:
                logger.warning('%d in %s at %s', line, path, commit.sha)
        _handle_exit(ethread)

    def get_linechanges(self, commit):
        linechanges = dict()

        for patch in _get_diff(self._pygit_repository.get(commit.sha)):
            path = patch.delta.new_file.path
            linechanges[path] = _get_linechanges(patch)

        return LineChanges(commit=commit, linechanges=linechanges)

    def get_message(self, sha):
        message = None

        commit = self.get_commit(sha)

        command = COMMANDS['messages']['commit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)
        for _, lines in parsers.GitLogParser.parse(ostream):
            message = Message(commit=commit, message='\n'.join(lines))
        _handle_exit(ethread)

        return message

    def get_messages(self, commits):
        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = COMMANDS['messages']['all'].format(filename=tfile.name)
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

    def get_moves(self, similarity=100):
        similarity = min(similarity, 100)

        command = COMMANDS['moves'].format(similarity=similarity)
        ostream, ethread = self._runner.run(command)

        for sha, lines in parsers.GitLogParser.parse(ostream):
            yield _get_moves(lines, self.get_commit(sha))

        _handle_exit(ethread)

    def get_patch(self, sha):
        patch = None

        commit = self.get_commit(sha)

        command = COMMANDS['patches']['commit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)
        for _, lines in parsers.GitLogParser.parse(ostream):
            patch = Patch(commit=commit, patch='\n'.join(lines))
        _handle_exit(ethread)

        return patch

    def get_patches(self, commits):
        tfile = None
        try:
            # Workaround for limit on command line arguments
            tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
            for commit in commits:
                tfile.write(f'{commit.sha}\n')
            tfile.close()

            command = COMMANDS['patches']['all'].format(filename=tfile.name)
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

    def _get_changes_for_sha(self, sha):
        commit = self.get_commit(sha)

        command = COMMANDS['changes']['commit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)

        for _, lines in parsers.GitLogParser.parse(ostream):
            yield _get_changes(lines, commit)
        _handle_exit(ethread)

    def _get_commits(self):
        key, command = self._get_key('commits'), COMMANDS['commits']['all']
        ostream, ethread = self._runner.run(command, key=key)
        for row in csv.reader(ostream):
            yield Commit(*row[:2], Developer(*row[2:4]))
        _handle_exit(ethread)

    def _get_commits_till_sha(self, sha):
        command = COMMANDS['commits']['limit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)
        for row in csv.reader(ostream):
            yield Commit(*row[:2], Developer(*row[2:4]))
        _handle_exit(ethread)

    def _get_deltas_for_sha(self, sha):
        commit = self.get_commit(sha)

        command = COMMANDS['deltas']['commit'].format(sha=sha)
        ostream, ethread = self._runner.run(command)

        for _, lines in parsers.GitLogParser.parse(ostream):
            yield _get_deltas(lines, commit)
        _handle_exit(ethread)

    def _get_key(self, item):
        return f'{self._project.name}_{self.get_version()}_{item}'
