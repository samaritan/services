import re

_SHA_RE = re.compile(r'^(?P<sha>[a-f0-9]{40})$')

def _get_snippets(stream):
    snippet = list()

    for line in stream:
        line = line.strip('\n')
        if line == '*':
            yield snippet
            snippet.clear()
        else:
            snippet.append(line)
    yield snippet


class GitLogParser:
    @staticmethod
    def parse(stream):
        _ = stream.readline()  # Discard the first separator line injected
        for snippet in _get_snippets(stream):
            yield (snippet[0], snippet[2:])
