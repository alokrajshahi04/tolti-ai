from enum import StrEnum


class Role(StrEnum):
    DRIVER = "driver"
    REVIEWER = "reviewer"
    WATCHER = "watcher"


ROLE_HIERARCHY = {
    Role.DRIVER: 3,
    Role.REVIEWER: 2,
    Role.WATCHER: 1,
}
