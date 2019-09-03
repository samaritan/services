from enum import Enum

class ChangeType(Enum):
    ADDED = 1
    COPIED = 5
    DELETED = 2
    MODIFIED = 3
    RENAMED = 4
    TYPECHANGE = 8
