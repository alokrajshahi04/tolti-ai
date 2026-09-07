from pydantic import BaseModel


class MembershipView(BaseModel):
    principal_id: str
    display_name: str
    role: str
    is_host: bool
