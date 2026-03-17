from enum import Enum 

class Role(str, Enum):
    SCHOOL_ADMIN = "school_admin"
    SUBSTITUTE = "substitute"
    SYSTEM_ADMIN = "system_admin"