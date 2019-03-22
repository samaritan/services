import logging
import re

from .models import Hunk

logger = logging.getLogger(__name__)

HUNKHEADER_RE = re.compile(r'(?:\n@@)')


def get_hunks(patches):
    hunks = list()

    for patch in patches:
        hunk = len(HUNKHEADER_RE.findall(patch.patch))
        hunks.append(Hunk(commit=patch.commit, hunk=hunk))

    return hunks
