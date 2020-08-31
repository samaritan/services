import logging
import re

from .models import Hunk

logger = logging.getLogger(__name__)

HUNKHEADER_RE = re.compile(r'(?:\n@@)')


def get_hunk(patch):
    hunk = len(HUNKHEADER_RE.findall(patch.patch))
    return Hunk(commit=patch.commit, hunk=hunk)
