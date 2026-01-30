from enum import Enum
from typing import Set, Dict

class Role(str, Enum):
    ENUMERATOR = "ENUMERATOR"
    SCREENER = "SCREENER"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"
    PATIENT = "PATIENT"

PERMS: Dict[Role, Set[str]] = {
    Role.ENUMERATOR: {
        "household:create", "household:edit",
        "people:create", "people:edit",
        "survey:write",
        "camps:view_assigned",
        "due:view_assigned",
        "reminders:write",
    },
    Role.SCREENER: {
        "encounter:start", "encounter:submit",
        "vitals:write", "tests:write",
        "tasks:create",
        "camps:view_assigned",
    },
    Role.CLINICIAN: {
        "queue:view", "unverified:view",
        "encounter:approve", "encounter:reject",
        "assessment:write",
        "tasks:close",
    },
    Role.ADMIN: {
        "admin:manage", "dashboards:view", "inventory:manage", "export:csv",
        "camps:create", "villages:manage", "assignments:manage",
    },
    Role.PATIENT: {
        "patient:view_self", "patient:totp", "camps:view_village",
    },
}

def has_perm(role: Role, perm: str) -> bool:
    return perm in PERMS.get(role, set())
