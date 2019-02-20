import re

_SHA_RE = re.compile(r'^(?P<sha>[a-f0-9]{40})$')

class GitLogParser:
    @staticmethod
    def parse(stream):
        lines, indices, shas = list(), list(), list()

        index = 0
        for line in stream:
            lines.append(line)
            match = _SHA_RE.match(line.strip('\n'))
            if match:
                indices.append(index)
                shas.append(match.groupdict().get('sha'))
            index += 1

        return lines, indices, shas
